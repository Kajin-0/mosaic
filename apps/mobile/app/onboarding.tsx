import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { useAuth } from '@/providers/AuthProvider';
import { theme } from '@/theme';

const steps = [
  ['01', 'Identity and relationship intent'],
  ['02', 'Hard constraints'],
  ['03', 'Relationship measurement'],
  ['04', 'Synthetic preference calibration'],
] as const;

export default function OnboardingPlaceholderScreen() {
  const router = useRouter();
  const { session, profile, loading, setLifecycleState } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (loading) return;
    if (!session) router.replace('/auth');
    else if (profile?.lifecycle_state === 'active') router.replace('/home');
  }, [loading, profile?.lifecycle_state, router, session]);

  async function completeOnboarding() {
    setBusy(true);
    setError(null);
    try {
      await setLifecycleState('active');
      router.replace('/home');
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : 'Unable to update profile state.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppScreen scroll>
      <View style={styles.header}>
        <Text style={styles.eyebrow}>ONBOARDING SHELL</Text>
        <Text style={styles.title}>Authenticated profile state is now persistent.</Text>
        <Text style={styles.body}>
          The measurement stages remain placeholders. This phase proves that onboarding lifecycle state belongs to the authenticated user and survives app restarts.
        </Text>
      </View>

      <View style={styles.steps}>
        {steps.map(([number, label]) => (
          <View key={number} style={styles.step}>
            <Text style={styles.stepNumber}>{number}</Text>
            <Text style={styles.stepLabel}>{label}</Text>
            <Text style={styles.stepStatus}>PLANNED</Text>
          </View>
        ))}
      </View>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <PrimaryButton disabled={loading || busy || !profile} onPress={() => void completeOnboarding()} testID="onboarding-complete">
        {busy ? 'Saving…' : 'Mark profile active'}
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
    fontSize: 32,
    lineHeight: 38,
    fontWeight: '800',
    letterSpacing: -0.7,
  },
  body: {
    color: theme.colors.muted,
    fontSize: 16,
    lineHeight: 24,
  },
  steps: {
    gap: theme.spacing.sm,
    marginBottom: theme.spacing.xl,
  },
  step: {
    minHeight: 76,
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.card,
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.md,
  },
  stepNumber: {
    width: 30,
    color: theme.colors.muted,
    fontSize: 13,
    fontWeight: '700',
  },
  stepLabel: {
    flex: 1,
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: '600',
  },
  stepStatus: {
    color: theme.colors.muted,
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.9,
  },
  error: {
    color: theme.colors.text,
    fontSize: 14,
    marginBottom: theme.spacing.md,
  },
});
