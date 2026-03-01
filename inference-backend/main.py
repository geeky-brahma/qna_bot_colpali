"""
GCP Cloud Functions handler for ColPali inference.
This function handles:
1. Loading PDFs from Cloud Storage by subject
2. Embedding queries with ColPali
3. Retrieving relevant pages
4. Generating answers with Flan-T5
"""

import functions_framework
from flask import Request, jsonify
import torch
import logging
import os
from typing import List, Dict
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from colpali_engine.models import ColPali, ColPaliProcessor
import tempfile
from pdf_handler import load_pdf_reader_class, extract_text_from_pdf

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Load environment variables from .env file in same directory as this script
env_path = os.path.join(os.path.dirname(__file__), '.env')
loaded = load_dotenv(env_path)
print(f"DEBUG: .env file path: {env_path}")
print(f"DEBUG: .env file exists: {os.path.exists(env_path)}")
print(f"DEBUG: load_dotenv() result: {loaded}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug: Log Gemini availability status
logger.info(f"GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
gemini_key_from_env = os.environ.get('GEMINI_API_KEY', '')
logger.info(f"GEMINI_API_KEY loaded from env: {'Yes (length: ' + str(len(gemini_key_from_env)) + ')' if gemini_key_from_env else 'No'}")
print(f"GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
print(f"GEMINI_API_KEY loaded from env: {'Yes (length: ' + str(len(gemini_key_from_env)) + ')' if gemini_key_from_env else 'No'}")

# Try to import OCR libraries
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
    logger.info("OCR libraries loaded successfully")
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR libraries not available. Install pdf2image and pytesseract for image PDF support.")

# Global model instances (loaded once and reused)
model = None
processor = None
qa_tokenizer = None
qa_model = None
storage_client = None
r2_client = None
gemini_model = None
gemini_initialized = False

SUBJECTS = {
    "Understanding and Appreciating Temple Architecture": "documents/temple_architecture.pdf",
    "Indian Knowledge Eco-system and Knowledge Model": "documents/indian_knowledge_ecosystem.pdf",
    "Indian Psychology and Integral Model of Human Experience": "documents/indian_psychology.pdf",
    "India Town Planning and Architecture": "documents/town_planning_architecture.pdf"
}

EMBEDDINGS = {
    "Understanding and Appreciating Temple Architecture": "embeddings/temple_architecture.pt",
    "Indian Knowledge Eco-system and Knowledge Model": "embeddings/indian_knowledge_ecosystem.pt",
    "Indian Psychology and Integral Model of Human Experience": "embeddings/indian_psychology.pt",
    "India Town Planning and Architecture": "embeddings/town_planning_architecture.pt"
}

R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME", "")
R2_ENDPOINT = os.environ.get("R2_ENDPOINT", "")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
R2_REGION = os.environ.get("R2_REGION", "auto")
DEBUG_SAVE_FILES = True  # Set to True to save downloaded files in debug_downloads/ for inspection
# DEBUG_SAVE_FILES = os.environ.get("DEBUG_SAVE_FILES", "false").lower() == "true"
DEBUG_FOLDER = os.path.join(os.path.dirname(__file__), "debug_downloads")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "vidore/colpali-v1.3"


def initialize_models():
    """Initialize ColPali, Gemini API, and Flan-T5 models (runs once on first request)."""
    global model, processor, qa_tokenizer, qa_model, r2_client, gemini_model, gemini_initialized

    if model is not None and r2_client is not None:
        return  # Already initialized

    logger.info("Initializing models...")
    logger.info(f"R2_BUCKET_NAME: {R2_BUCKET_NAME[:10] if R2_BUCKET_NAME else 'MISSING'}...")
    logger.info(f"R2_ENDPOINT: {R2_ENDPOINT[:30] if R2_ENDPOINT else 'MISSING'}...")

    try:
        # Initialize ColPali model for query embedding
        model = ColPali.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            device_map=DEVICE,
            attn_implementation="flash_attention_2" if DEVICE == "cuda" else "eager",
        ).eval()
        processor = ColPaliProcessor.from_pretrained(MODEL_NAME)
        logger.info("✓ ColPali model loaded")

        # Initialize Gemini API for QA (primary)
        # Re-read from env in case it wasn't loaded at module import time
        gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        if gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_api_key)
                gemini_model = genai.GenerativeModel('gemma-3-27b-it')
                gemini_initialized = True
                logger.info("✓ Gemini API configured (primary QA model)")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API: {str(e)}. Will use Flan-T5 fallback.")
                gemini_initialized = False
        else:
            if not GEMINI_AVAILABLE:
                logger.warning("google.generativeai package not installed. Install with: pip install google-generativeai")
            if not gemini_api_key:
                logger.warning("GEMINI_API_KEY not found in environment variables.")
            logger.warning("Will use Flan-T5 fallback.")
            gemini_initialized = False

        # Initialize Flan-T5 for QA (fallback)
        qa_model_name = "google/flan-t5-small"
        qa_tokenizer = AutoTokenizer.from_pretrained(qa_model_name)
        qa_model = AutoModelForSeq2SeqLM.from_pretrained(qa_model_name).to(DEVICE).eval()
        logger.info("✓ Flan-T5 model loaded (fallback QA model)")

        # Initialize R2 client
        if not all([R2_BUCKET_NAME, R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
            raise ValueError(
                "R2 backend required but missing env vars: "
                "R2_BUCKET_NAME, R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY"
            )

        r2_client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            region_name=R2_REGION,
        )
        logger.info("✓ R2 storage client initialized")

    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        raise


def get_pdf_path(subject: str) -> str:
    """Get GCS path for subject PDF."""
    return SUBJECTS.get(subject, f"documents/{subject.lower().replace(' ', '_')}.pdf")


def get_embeddings_path(subject: str) -> str:
    """Get R2 path for subject embeddings (.pt file)."""
    return EMBEDDINGS.get(subject, f"embeddings/{subject.lower().replace(' ', '_')}_embeddings.pt")


def download_blob_from_gcs(gcs_path: str, suffix: str) -> str:
    """Download a blob from R2 to a local file (temp or debug folder)."""
    if not storage_object_exists(gcs_path):
        raise FileNotFoundError(f"File not found in R2: {gcs_path}")

    if DEBUG_SAVE_FILES:
        # Save to debug folder with meaningful name
        os.makedirs(DEBUG_FOLDER, exist_ok=True)
        # Use sanitized version of R2 path as filename
        safe_name = gcs_path.replace("/", "_").replace("\\", "_")
        local_path = os.path.join(DEBUG_FOLDER, safe_name)
        
        with open(local_path, "wb") as output_file:
            r2_client.download_fileobj(R2_BUCKET_NAME, gcs_path, output_file)
        
        logger.info(f"Downloaded file from R2 (DEBUG MODE): {gcs_path} -> {local_path}")
        return local_path
    else:
        # Use temp file as before
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.close()

        with open(temp_file.name, "wb") as output_file:
            r2_client.download_fileobj(R2_BUCKET_NAME, gcs_path, output_file)

        logger.info(f"Downloaded file from R2: {gcs_path}")
        return temp_file.name


def storage_object_exists(path: str) -> bool:
    """Check if object exists in R2."""
    try:
        r2_client.head_object(Bucket=R2_BUCKET_NAME, Key=path)
        return True
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise


def generate_answer_with_fallback(query: str, context: str) -> str:
    """
    Generate answer using Gemini API with Flan-T5 fallback.
    Tries Gemini first, falls back to Flan-T5 on rate limit or API errors.
    """
    prompt = (
        "Answer the question using ONLY the context below. "
        "If the answer is not present, say: 'I could not find that in the retrieved pages.'\n\n"
        f"Question: {query}\n\n"
        f"Context:\n{context}\n\n"
        "Answer:"
    )

    # Try Gemini API first
    if gemini_initialized and gemini_model:
        try:
            logger.info("Generating answer with Gemini API...")
            print("Generating answer with Gemini API...")
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.3,
                )
            )
            answer = response.text.strip()
            logger.info("✓ Answer generated with Gemini API")
            return answer if answer else "I could not find that in the retrieved pages."
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Error with Gemini API: {error_msg}. Falling back to Flan-T5.")
            # Check for rate limit or API errors
            if "rate" in error_msg or "quota" in error_msg or "429" in error_msg:
                logger.warning(f"Gemini API rate limit/quota exceeded: {str(e)}. Falling back to Flan-T5.")
            else:
                logger.warning(f"Gemini API error: {str(e)}. Falling back to Flan-T5.")
    
    # Fallback to Flan-T5
    try:
        print("Generating answer with Flan-T5 (fallback)...")
        logger.info("Generating answer with Flan-T5 (fallback)...")
        llm_inputs = qa_tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(DEVICE)

        with torch.inference_mode():
            llm_output = qa_model.generate(
                **llm_inputs,
                max_new_tokens=180,
                do_sample=False,
                num_beams=3
            )

        answer = qa_tokenizer.decode(llm_output[0], skip_special_tokens=True)
        logger.info("✓ Answer generated with Flan-T5 (fallback)")
        return answer if answer.strip() else "I could not find that in the retrieved pages."
    except Exception as e:
        logger.error(f"Error generating answer with Flan-T5 fallback: {str(e)}")
        raise


@functions_framework.http
def colpali_query(request: Request):
    """
    HTTP Cloud Function for RAG query processing.
    
    Request body:
    {
        "query": "What is...",
        "subject": "Mathematics",
        "pdf_path": "documents/mathematics.pdf"  (optional, uses default if not provided)
    }
    """
    pdf_path = None
    embeddings_path = None

    try:
        # Initialize models on first call
        initialize_models()

        # Parse request
        request_json = request.get_json(silent=True) or {}
        query = request_json.get("query", "").strip()
        subject = request_json.get("subject", "").strip()

        if not query:
            return jsonify({"error": "Query is required"}), 400
        if not subject:
            return jsonify({"error": "Subject is required"}), 400

        logger.info(f"Processing query: {query[:50]}... | Subject: {subject}")
        print(f"Processing query: {query[:50]}... | Subject: {subject}")

        # Download PDF from GCS
        pdf_gcs_path = get_pdf_path(subject)
        embeddings_gcs_path = get_embeddings_path(subject)
        print(f"Resolved PDF GCS path: {pdf_gcs_path}")
        print(f"Resolved embeddings GCS path: {embeddings_gcs_path}")

        pdf_path = download_blob_from_gcs(pdf_gcs_path, suffix=".pdf")
        embeddings_path = download_blob_from_gcs(embeddings_gcs_path, suffix=".pt")

        try:
            # Load PDF and extract embedding-friendly content
            PdfReader = load_pdf_reader_class()
            pdf_reader = PdfReader(pdf_path)
            total_pages = len(pdf_reader.pages)

            logger.info(f"PDF loaded: {total_pages} pages")

            # Convert pages to images and get embeddings (simplified for now)
            # In production, you'd use the full ImageProcessor
            # For now, we'll extract text and use it for retrieval

            # Step 1: Get query embedding with ColPali
            logger.info("Getting query embedding...")
            batch_queries = processor.process_queries([query]).to(DEVICE)

            with torch.inference_mode():
                query_embeddings = model(**batch_queries)

            # Step 2: Load precomputed page embeddings for selected subject
            image_embeddings = torch.load(embeddings_path, map_location=DEVICE)

            # Step 3: Retrieve top pages using ColPali scoring
            relevant_pages = retrieve_relevant_pages(
                query_embeddings=query_embeddings,
                image_embeddings=image_embeddings,
                top_k=3
            )

            logger.info(f"Retrieved pages: {relevant_pages}")

            # Step 4: Build context and generate answer with Gemini or Flan-T5
            context = build_context(pdf_reader, relevant_pages, max_chars_per_page=1500, pdf_path=pdf_path)
            answer = generate_answer_with_fallback(query, context)

            logger.info(f"Answer generated successfully")

            return jsonify({
                "answer": answer if answer.strip() else "I could not find that in the retrieved pages.",
                "source_pages": [p + 1 for p in relevant_pages],
                "subject": subject,
                "total_pages": total_pages
            })

        finally:
            # Clean up temp files (skip if debug mode enabled)
            if not DEBUG_SAVE_FILES:
                if pdf_path and os.path.exists(pdf_path):
                    os.remove(pdf_path)
                if embeddings_path and os.path.exists(embeddings_path):
                    os.remove(embeddings_path)
            else:
                logger.info(f"Debug mode: keeping files at {pdf_path} and {embeddings_path}")

    except Exception as e:
        logger.error(f"Error in colpali_query: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@functions_framework.http
def health(request: Request):
    """Health check endpoint."""
    try:
        initialize_models()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


def retrieve_relevant_pages(query_embeddings, image_embeddings, top_k: int = 3) -> List[int]:
    """
    Retrieve top-k most relevant pages with ColPali multi-vector scoring.
    """
    scores = processor.score_multi_vector(query_embeddings, image_embeddings)
    query_scores = scores[0]

    if query_scores.numel() == 0:
        return []

    top_k = min(top_k, len(query_scores))
    _, top_indices = torch.topk(query_scores, top_k)

    return [idx.item() for idx in top_indices]


def ocr_pdf_page(pdf_path: str, page_num: int) -> str:
    """Extract text from a PDF page using OCR."""
    if not OCR_AVAILABLE:
        return "[OCR not available - install pdf2image and pytesseract]"
    
    try:
        # Convert specific page to image (page_num is 0-indexed internally, but pdf2image uses 1-indexed)
        images = convert_from_path(
            pdf_path, 
            first_page=page_num + 1, 
            last_page=page_num + 1,
            dpi=200
        )
        
        if not images:
            return "[OCR failed - no image generated]"
        
        # OCR the image
        text = pytesseract.image_to_string(images[0], lang='eng')
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR failed for page {page_num + 1}: {str(e)}")
        return f"[OCR failed: {str(e)}]"


def build_context(
    pdf_reader,
    page_numbers: List[int],
    max_chars_per_page: int = 1500,
    pdf_path: str = None
) -> str:
    """Build context string from selected pages with OCR fallback."""
    contexts = []
    for page_num in page_numbers:
        try:
            page = pdf_reader.pages[page_num]
            text = (page.extract_text() or "").strip()
            
            # If no text extracted and OCR is available, try OCR
            if not text and OCR_AVAILABLE and pdf_path:
                logger.info(f"Page {page_num + 1}: No text found, attempting OCR...")
                text = ocr_pdf_page(pdf_path, page_num)
                if text and text not in ["[OCR not available - install pdf2image and pytesseract]", "[OCR failed - no image generated]"]:
                    logger.info(f"Page {page_num + 1}: OCR extracted {len(text)} characters")
            
            if not text:
                text = "[No extractable text on this page]"
            
            contexts.append(f"Page {page_num + 1}:\n{text[:max_chars_per_page]}")
        except Exception as e:
            logger.error(f"Error processing page {page_num + 1}: {str(e)}")
            contexts.append(f"Page {page_num + 1}: [Error: {str(e)}]")

    return "\n\n".join(contexts)
