import type { PropsWithChildren } from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { theme } from '@/theme';

type AppScreenProps = PropsWithChildren<{
  scroll?: boolean;
}>;

export function AppScreen({ children, scroll = false }: AppScreenProps) {
  const content = <View style={styles.content}>{children}</View>;

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'right', 'bottom', 'left']}>
      {scroll ? (
        <ScrollView contentContainerStyle={styles.scrollContent}>{content}</ScrollView>
      ) : (
        content
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    flex: 1,
    width: '100%',
    maxWidth: 640,
    alignSelf: 'center',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.lg,
  },
  scrollContent: {
    flexGrow: 1,
  },
});
