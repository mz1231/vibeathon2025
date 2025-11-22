"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import {
  generateMockConversation,
  type Profile,
} from "@/lib/mockData";
import { Button, Card } from "@/components/ui";
import Sidebar from "@/components/Sidebar";

export default function ProfilesPage() {
  const router = useRouter();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfiles, setSelectedProfiles] = useState<string[]>([]);

  useEffect(() => {
    // Load created profiles from localStorage
    const stored = localStorage.getItem('createdProfiles');
    if (stored) {
      setProfiles(JSON.parse(stored));
    }
  }, []);

  const handleProfileClick = (profileId: string) => {
    if (selectedProfiles.includes(profileId)) {
      // Deselect
      setSelectedProfiles(selectedProfiles.filter(id => id !== profileId));
    } else if (selectedProfiles.length < 2) {
      // Select (max 2)
      setSelectedProfiles([...selectedProfiles, profileId]);
    } else {
      // Already have 2 selected, replace the first one
      setSelectedProfiles([selectedProfiles[1], profileId]);
    }
  };

  const handleSimulate = () => {
    if (selectedProfiles.length !== 2) {
      alert('Please select exactly 2 profiles to simulate');
      return;
    }

    const profileA = profiles.find(p => p.id === selectedProfiles[0])!;
    const profileB = profiles.find(p => p.id === selectedProfiles[1])!;

    // Generate conversation between the two selected profiles
    const conversation = generateMockConversation(profileA, profileB);
    localStorage.setItem("currentConversation", JSON.stringify(conversation));
    router.push("/replay");
  };

  const selectedProfileA = profiles.find(p => p.id === selectedProfiles[0]);
  const selectedProfileB = profiles.find(p => p.id === selectedProfiles[1]);

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
              Select two profiles to simulate a conversation and analyze compatibility
            </p>
          </div>

          {/* Selection Status & Simulate Button */}
          {profiles.length >= 2 && (
            <Card className="p-4 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-sm text-[var(--text-secondary)]">
                    Selected profiles:
                  </span>

                  {selectedProfileA ? (
                    <div className="flex items-center gap-2">
                      <div
                        className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-medium"
                        style={{ backgroundColor: selectedProfileA.color }}
                      >
                        {selectedProfileA.name[0]}
                      </div>
                      <span className="text-sm font-medium text-[var(--text-primary)]">
                        {selectedProfileA.name}
                      </span>
                    </div>
                  ) : (
                    <span className="text-sm text-[var(--text-secondary)]">—</span>
                  )}

                  <span className="text-[var(--text-secondary)]">×</span>

                  {selectedProfileB ? (
                    <div className="flex items-center gap-2">
                      <div
                        className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-medium"
                        style={{ backgroundColor: selectedProfileB.color }}
                      >
                        {selectedProfileB.name[0]}
                      </div>
                      <span className="text-sm font-medium text-[var(--text-primary)]">
                        {selectedProfileB.name}
                      </span>
                    </div>
                  ) : (
                    <span className="text-sm text-[var(--text-secondary)]">—</span>
                  )}
                </div>

                <Button
                  variant="primary"
                  size="md"
                  onClick={handleSimulate}
                  disabled={selectedProfiles.length !== 2}
                >
                  Simulate Conversation →
                </Button>
              </div>
            </Card>
          )}

          {/* Profile Grid */}
          {profiles.length === 0 ? (
            <Card className="p-12 text-center">
              <div className="max-w-md mx-auto space-y-4">
                <div className="text-lg font-medium text-[var(--text-primary)]">
                  No profiles created yet
                </div>
                <p className="text-sm text-[var(--text-secondary)]">
                  Create at least 2 profiles to start simulating conversations
                </p>
                <Button
                  variant="primary"
                  size="md"
                  onClick={() => router.push('/profile')}
                >
                  Create Profile
                </Button>
              </div>
            </Card>
          ) : profiles.length === 1 ? (
            <Card className="p-12 text-center">
              <div className="max-w-md mx-auto space-y-4">
                <div className="text-lg font-medium text-[var(--text-primary)]">
                  Create one more profile
                </div>
                <p className="text-sm text-[var(--text-secondary)]">
                  You need at least 2 profiles to simulate a conversation
                </p>
                <Button
                  variant="primary"
                  size="md"
                  onClick={() => router.push('/profile')}
                >
                  Create Another Profile
                </Button>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {profiles.map((profile) => {
                const isSelected = selectedProfiles.includes(profile.id);
                const selectionIndex = selectedProfiles.indexOf(profile.id);

                return (
                  <Card
                    key={profile.id}
                    className={`relative p-5 flex flex-col cursor-pointer transition-all ${
                      isSelected
                        ? 'ring-2 ring-[var(--accent)] bg-[var(--accent)]/5'
                        : 'hover:border-[var(--accent)]'
                    }`}
                    onClick={() => handleProfileClick(profile.id)}
                  >
                    {isSelected && (
                      <div className="absolute top-3 right-3 w-6 h-6 bg-[var(--accent)] text-white rounded-full flex items-center justify-center text-xs font-medium">
                        {selectionIndex + 1}
                      </div>
                    )}

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
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
