import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { useAuth } from '@/providers/AuthProvider';
import { theme } from '@/theme';

const modules = [
  ['Profile', 'Phase 2', 'Authenticated and persisted user lifecycle state'],
  ['Calibration', 'Phase 4+', 'Adaptive measurement and synthetic trials'],
  ['Matches', 'Later', 'Directional attraction and dyadic ranking'],
] as const;

export default function HomePlaceholderScreen() {
  const router = useRouter();
  const { session, profile, loading, signOut } = useAuth();
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!session) router.replace('/auth');
    else if (profile && profile.lifecycle_state !== 'active') router.replace('/onboarding');
  }, [loading, profile, router, session]);

  async function handleSignOut() {
    setBusy(true);
    try {
      await signOut();
      router.replace('/auth');
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppScreen scroll>
      <View style={styles.header}>
        <Text style={styles.eyebrow}>PROTOTYPE HOME</Text>
        <Text style={styles.title}>Authenticated mobile shell online.</Text>
        <Text style={styles.body}>
          The private profile row is persisted through Supabase and protected by owner-only row-level security.
        </Text>
      </View>

      <View style={styles.statusBox}>
        <Text style={styles.statusLabel}>PROFILE STATE</Text>
        <Text style={styles.statusValue}>{profile?.lifecycle_state ?? 'loading'}</Text>
        <Text style={styles.statusMeta}>Version {profile?.profile_version ?? '—'}</Text>
        <Text style={styles.statusMeta}>User {session?.user.id.slice(0, 8) ?? '—'}…</Text>
      </View>

      <View style={styles.moduleList}>
        {modules.map(([name, phase, description]) => (
          <View key={name} style={styles.card}>
            <View style={styles.cardTopline}>
              <Text style={styles.cardTitle}>{name}</Text>
              <Text style={styles.phase}>{phase}</Text>
            </View>
            <Text style={styles.cardBody}>{description}</Text>
          </View>
        ))}
      </View>

      <PrimaryButton disabled={busy} onPress={() => void handleSignOut()} testID="home-sign-out">
        {busy ? 'Signing out…' : 'Sign out'}
      </PrimaryButton>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  header: {
    gap: theme.spacing.md,
    marginBottom: theme.spacing.xl,
  },
  eyebrow: {
    color: theme.colors.muted,
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1.3,
  },
  title: {
    color: theme.colors.text,
    fontSize: 36,
    lineHeight: 42,
    fontWeight: '800',
    letterSpacing: -0.8,
  },
  body: {
    color: theme.colors.muted,
    fontSize: 16,
    lineHeight: 24,
  },
  statusBox: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
    gap: theme.spacing.xs,
    marginBottom: theme.spacing.xl,
  },
  statusLabel: {
    color: theme.colors.muted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.1,
  },
  statusValue: {
    color: theme.colors.text,
    fontSize: 20,
    fontWeight: '700',
  },
  statusMeta: {
    color: theme.colors.muted,
    fontSize: 13,
  },
  moduleList: {
    gap: theme.spacing.sm,
    marginBottom: theme.spacing.xl,
  },
  card: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
    gap: theme.spacing.sm,
  },
  cardTopline: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: theme.spacing.md,
  },
  cardTitle: {
    color: theme.colors.text,
    fontSize: 20,
    fontWeight: '700',
  },
  phase: {
    color: theme.colors.muted,
    fontSize: 12,
    fontWeight: '700',
  },
  cardBody: {
    color: theme.colors.muted,
    fontSize: 15,
    lineHeight: 22,
  },
});
