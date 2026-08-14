import type { Session } from '@supabase/supabase-js';
import type { ReactNode } from 'react';
import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { AppState, Platform } from 'react-native';

import { supabase } from '@/lib/supabase';

export type ProfileLifecycleState = 'onboarding' | 'active' | 'paused' | 'deleted';

export type Profile = {
  user_id: string;
  lifecycle_state: ProfileLifecycleState;
  profile_version: number;
  created_at: string;
  updated_at: string;
};

type AuthContextValue = {
  session: Session | null;
  profile: Profile | null;
  loading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<{ requiresEmailConfirmation: boolean }>;
  signOut: () => Promise<void>;
  setLifecycleState: (state: ProfileLifecycleState) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

async function fetchOrCreateProfile(userId: string): Promise<Profile> {
  const existing = await supabase
    .from('profiles')
    .select('user_id,lifecycle_state,profile_version,created_at,updated_at')
    .eq('user_id', userId)
    .maybeSingle<Profile>();

  if (existing.error) {
    throw existing.error;
  }

  if (existing.data) {
    return existing.data;
  }

  const created = await supabase
    .from('profiles')
    .insert({ user_id: userId, lifecycle_state: 'onboarding' })
    .select('user_id,lifecycle_state,profile_version,created_at,updated_at')
    .single<Profile>();

  if (!created.error && created.data) {
    return created.data;
  }

  if (created.error?.code === '23505') {
    const raced = await supabase
      .from('profiles')
      .select('user_id,lifecycle_state,profile_version,created_at,updated_at')
      .eq('user_id', userId)
      .single<Profile>();

    if (!raced.error && raced.data) {
      return raced.data;
    }
  }

  throw created.error ?? new Error('Unable to initialize Mosaic profile.');
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    void supabase.auth.getSession().then(({ data, error: sessionError }) => {
      if (!mounted) return;
      if (sessionError) setError(sessionError.message);
      setSession(data.session);
      if (!data.session) setLoading(false);
    });

    const { data } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      if (mounted) setSession(nextSession);
    });

    return () => {
      mounted = false;
      data.subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (Platform.OS === 'web') return undefined;

    const subscription = AppState.addEventListener('change', (state) => {
      if (state === 'active') {
        supabase.auth.startAutoRefresh();
      } else {
        supabase.auth.stopAutoRefresh();
      }
    });

    return () => subscription.remove();
  }, []);

  useEffect(() => {
    let cancelled = false;

    if (!session?.user.id) {
      setProfile(null);
      setLoading(false);
      return undefined;
    }

    setLoading(true);
    setError(null);

    void fetchOrCreateProfile(session.user.id)
      .then((nextProfile) => {
        if (!cancelled) setProfile(nextProfile);
      })
      .catch((profileError: unknown) => {
        if (!cancelled) {
          setError(profileError instanceof Error ? profileError.message : 'Unable to load profile.');
          setProfile(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [session?.user.id]);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      profile,
      loading,
      error,
      async signIn(email, password) {
        setError(null);
        const result = await supabase.auth.signInWithPassword({ email, password });
        if (result.error) throw result.error;
      },
      async signUp(email, password) {
        setError(null);
        const result = await supabase.auth.signUp({ email, password });
        if (result.error) throw result.error;
        return { requiresEmailConfirmation: !result.data.session };
      },
      async signOut() {
        const result = await supabase.auth.signOut();
        if (result.error) throw result.error;
        setProfile(null);
      },
      async setLifecycleState(state) {
        if (!session?.user.id) throw new Error('No authenticated Mosaic session.');

        const result = await supabase
          .from('profiles')
          .update({ lifecycle_state: state })
          .eq('user_id', session.user.id)
          .select('user_id,lifecycle_state,profile_version,created_at,updated_at')
          .single<Profile>();

        if (result.error) throw result.error;
        setProfile(result.data);
      },
    }),
    [error, loading, profile, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider.');
  return context;
}
