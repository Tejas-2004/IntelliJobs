'use client';

import { useUser } from '@clerk/nextjs';
import { useEffect } from 'react';

export default function UserSyncer() {
  const { user } = useUser();

  useEffect(() => {
    if (!user?.id) return;

    const syncUser = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/sync-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ userId: user.id }),
        });

        const data = await res.json();
        console.log('User sync status:', data);
      } catch (error) {
        console.error('Sync failed:', error);
      }
    };

    syncUser();
  }, [user]);

  return null; // This component renders nothing
}
