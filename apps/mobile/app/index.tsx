import { useRouter } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { theme } from '@/theme';

export default function EntryScreen() {
  const router = useRouter();

  return (
    <AppScreen>
      <View style={styles.badge}>
        <Text style={styles.badgeText}>PHASE 1 · MOBILE SHELL</Text>
      </View>

      <View style={styles.hero}>
        <Text style={styles.wordmark}>Mosaic</Text>
        <Text style={styles.headline}>Built for relationships that are meant to last.</Text>
        <Text style={styles.body}>
          This build establishes the mobile navigation and interface boundary before authentication,
          persistence, or matching logic is introduced.
        </Text>
      </View>

      <PrimaryButton onPress={() => router.push('/auth')} testID="entry-continue">
        Continue
      </PrimaryButton>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 7,
  },
  badgeText: {
    color: theme.colors.muted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1.1,
  },
  hero: {
    flex: 1,
    justifyContent: 'center',
    gap: theme.spacing.md,
  },
  wordmark: {
    color: theme.colors.text,
    fontSize: 22,
    fontWeight: '700',
  },
  headline: {
    maxWidth: 520,
    color: theme.colors.text,
    fontSize: 42,
    lineHeight: 48,
    fontWeight: '800',
    letterSpacing: -1.2,
  },
  body: {
    maxWidth: 520,
    color: theme.colors.muted,
    fontSize: 17,
    lineHeight: 25,
  },
});
