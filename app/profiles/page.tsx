"use client";

import { useRouter } from "next/navigation";
import {
  mockProfiles,
  currentUser,
  generateMockConversation,
  type Profile,
} from "@/lib/mockData";
import { Button, Card, Input } from "@/components/ui";
import Sidebar from "@/components/Sidebar";

export default function ProfilesPage() {
  const router = useRouter();

  const handleSimulate = (match: Profile) => {
    // Generate conversation between YOU and the match
    const conversation = generateMockConversation(
      currentUser,
      match
    );
    localStorage.setItem("currentConversation", JSON.stringify(conversation));
    router.push("/replay");
  };

  return (
    <div className="flex h-screen bg-[var(--bg)]">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-12 py-10">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold mb-2 text-[var(--text-primary)]">
              Match Compatibility Simulator
            </h1>
            <p className="text-sm text-[var(--text-secondary)]">
              Browse profiles and simulate conversations to discover compatibility
            </p>
          </div>

          {/* Search Bar */}
          <div className="mb-8">
            <Input
              placeholder="Search profiles..."
              className="max-w-md"
            />
          </div>

          {/* Profile Grid */}
          <div className="grid grid-cols-3 gap-4">
            {mockProfiles.map((profile) => (
              <Card
                key={profile.id}
                className="relative p-5 flex flex-col"
              >
                {/* Avatar */}
                <div className="mb-4">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center text-white text-base font-medium"
                    style={{ backgroundColor: profile.color }}
                  >
                    {profile.name[0]}
                  </div>
                </div>

                {/* Name */}
                <h3 className="text-sm font-medium text-[var(--text-primary)] mb-1">
                  {profile.name}
                </h3>

                {/* Bio snippet */}
                <p className="text-xs text-[var(--text-secondary)] mb-4 line-clamp-2 flex-1">
                  {profile.bio || 'No bio available'}
                </p>

                {/* Simulate Button */}
                <Button
                  variant="secondary"
                  size="sm"
                  className="w-full text-xs"
                  onClick={() => handleSimulate(profile)}
                >
                  Simulate →
                </Button>
              </Card>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
