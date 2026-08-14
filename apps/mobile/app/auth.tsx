import { useRouter } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { theme } from '@/theme';

export default function AuthPlaceholderScreen() {
  const router = useRouter();

  return (
    <AppScreen>
      <View style={styles.content}>
        <Text style={styles.eyebrow}>ACCOUNT</Text>
        <Text style={styles.title}>Authentication boundary ready.</Text>
        <Text style={styles.body}>
          Supabase authentication arrives in Phase 2. For Phase 1, this local test session proves the
          navigation contract without inventing temporary authentication state.
        </Text>
      </View>

      <PrimaryButton onPress={() => router.push('/onboarding')} testID="auth-local-session">
        Use local test session
      </PrimaryButton>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  content: {
    flex: 1,
    justifyContent: 'center',
    gap: theme.spacing.md,
  },
  eyebrow: {
    color: theme.colors.muted,
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1.3,
  },
  title: {
    color: theme.colors.text,
    fontSize: 34,
    lineHeight: 40,
    fontWeight: '800',
    letterSpacing: -0.8,
  },
  body: {
    color: theme.colors.muted,
    fontSize: 17,
    lineHeight: 25,
  },
});
