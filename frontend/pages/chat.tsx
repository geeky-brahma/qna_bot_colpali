import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/router";
import { useState } from "react";
import ChatInterface from "@/components/ChatInterface";

const SUBJECTS = [
  "Understanding and Appreciating Temple Architecture",
  "Indian Knowledge Eco-system and Knowledge Model",
  "Indian Psychology and Integral Model of Human Experience",
  "India Town Planning and Architecture"
];

export default function Chat() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);

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

  if (status === "unauthenticated") {
    router.push("/");
    return null;
  }

  if (!selectedSubject) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="flex justify-between items-center mb-8 mt-8">
            <h1 className="text-3xl font-bold text-white">Select a Subject</h1>
            <button
              onClick={() => signOut({ redirect: false })}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition"
            >
              Sign out
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-xl p-8">
            <p className="text-gray-700 mb-6">
              Welcome, <span className="font-semibold">{session?.user?.email}</span>!
            </p>
            <p className="text-gray-600 mb-8">
              Choose a subject to start asking questions:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {SUBJECTS.map((subject) => (
                <button
                  key={subject}
                  onClick={() => setSelectedSubject(subject)}
                  className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-6 px-6 rounded-lg transition transform hover:scale-105 shadow-md"
                >
                  {subject}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ChatInterface
      subject={selectedSubject}
      userEmail={session?.user?.email || ""}
      onBack={() => setSelectedSubject(null)}
      onSignOut={() => signOut({ redirect: false })}
    />
  );
}
