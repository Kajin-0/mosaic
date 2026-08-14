import { useRouter } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { theme } from '@/theme';

const steps = [
  ['01', 'Identity and relationship intent'],
  ['02', 'Hard constraints'],
  ['03', 'Relationship measurement'],
  ['04', 'Synthetic preference calibration'],
] as const;

export default function OnboardingPlaceholderScreen() {
  const router = useRouter();

  return (
    <AppScreen scroll>
      <View style={styles.header}>
        <Text style={styles.eyebrow}>ONBOARDING SHELL</Text>
        <Text style={styles.title}>One inference pipeline, introduced in controlled stages.</Text>
        <Text style={styles.body}>
          The controls are placeholders. Phase 2 adds identity persistence; later phases replace each
          stage with versioned measurement instruments.
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

      <PrimaryButton onPress={() => router.replace('/home')} testID="onboarding-complete">
        Enter prototype home
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
});
