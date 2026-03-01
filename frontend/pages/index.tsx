import { useSession, signIn } from "next-auth/react";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function Login() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session) {
      router.push("/chat");
    }
  }, [session, router]);

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-center mb-2 text-gray-800">
          RAG System
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Retrieval-Augmented Generation for Document Q&A
        </p>

        <button
          onClick={() => signIn("google", { redirect: false })}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition flex items-center justify-center gap-2"
        >
          <svg
            className="w-5 h-5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M15.545 6.558a9.42 9.42 0 0 1 .139 1.626c0 2.449-.356 4.68-1.7 6.008 0 0-1.4 1.369-4.128 1.369-2.603 0-4.55-1.266-4.55-3.565 0-2.408 1.87-4.063 4.467-4.063.342 0 .735.043 1.063.137 0-.502-.283-1.336-.926-1.336-2.237 0-5.166 1.98-5.166 4.778 0 2.502 1.333 4.63 4.744 4.63 3.923 0 5.744-2.165 5.744-4.652 0-.34-.023-.678-.065-.99-.196-.413-.664-.646-1.247-.646h-.183c-.917 0-1.6.37-1.6 1.07v.727h-.006c-.305-1.08-1.895-2.086-3.702-2.086-1.923 0-3.638 1.049-3.638 2.595 0 1.104.774 2.325 2.772 2.325h.142c.957 0 1.379-.263 1.379-.910v-.742c0-.696-1.desimal 8-2.172-1.88-2.172-.4 0-.779.063-1.047.226-.531.315-1.337 1.259-1.337 2.822 0 1.224.505 2.082 1.644 2.082.923 0 1.738-.521 1.738-1.437V8.5c0-.916.516-1.334 1.632-1.334 1.385 0 2.127.686 2.127 1.973v.71z" />
          </svg>
          Sign in with Google
        </button>

        <div className="mt-8 text-center text-sm text-gray-600">
          <p>By signing in, you agree to our Terms of Service</p>
        </div>
      </div>
    </div>
  );
}
