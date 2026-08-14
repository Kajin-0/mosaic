import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, TextInput, View } from 'react-native';

import { AppScreen } from '@/components/AppScreen';
import { PrimaryButton } from '@/components/PrimaryButton';
import { useAuth } from '@/providers/AuthProvider';
import { theme } from '@/theme';

export default function AuthScreen() {
  const router = useRouter();
  const { session, profile, loading, error: authError, signIn, signUp } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (loading || !session || !profile) return;
    router.replace(profile.lifecycle_state === 'active' ? '/home' : '/onboarding');
  }, [loading, profile, router, session]);

  const credentialsReady = email.trim().length > 3 && password.length >= 6;

  async function handleSignIn() {
    setBusy(true);
    setMessage(null);
    try {
      await signIn(email.trim(), password);
    } catch (signInError) {
      setMessage(signInError instanceof Error ? signInError.message : 'Unable to sign in.');
    } finally {
      setBusy(false);
    }
  }

  async function handleSignUp() {
    setBusy(true);
    setMessage(null);
    try {
      const result = await signUp(email.trim(), password);
      if (result.requiresEmailConfirmation) {
        setMessage('Account created. Confirm your email before signing in.');
      }
    } catch (signUpError) {
      setMessage(signUpError instanceof Error ? signUpError.message : 'Unable to create account.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppScreen scroll>
      <View style={styles.content}>
        <Text style={styles.eyebrow}>ACCOUNT</Text>
        <Text style={styles.title}>Create or resume your Mosaic account.</Text>
        <Text style={styles.body}>
          Phase 2 stores authentication with Supabase and creates one private profile row owned by your account.
        </Text>

        <View style={styles.form}>
          <TextInput
            accessibilityLabel="Email address"
            autoCapitalize="none"
            autoComplete="email"
            keyboardType="email-address"
            onChangeText={setEmail}
            placeholder="Email"
            placeholderTextColor={theme.colors.muted}
            style={styles.input}
            value={email}
          />
          <TextInput
            accessibilityLabel="Password"
            autoCapitalize="none"
            autoComplete="password"
            onChangeText={setPassword}
            placeholder="Password"
            placeholderTextColor={theme.colors.muted}
            secureTextEntry
            style={styles.input}
            value={password}
          />
        </View>

        {(message ?? authError) ? <Text style={styles.message}>{message ?? authError}</Text> : null}
      </View>

      <View style={styles.actions}>
        <PrimaryButton disabled={!credentialsReady || busy} onPress={() => void handleSignIn()} testID="auth-sign-in">
          {busy ? 'Working…' : 'Sign in'}
        </PrimaryButton>
        <PrimaryButton disabled={!credentialsReady || busy} onPress={() => void handleSignUp()} testID="auth-sign-up">
          Create account
        </PrimaryButton>
      </View>
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
  form: {
    gap: theme.spacing.sm,
    marginTop: theme.spacing.md,
  },
  input: {
    minHeight: 54,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.button,
    backgroundColor: theme.colors.surface,
    color: theme.colors.text,
    fontSize: 16,
    paddingHorizontal: theme.spacing.md,
  },
  message: {
    color: theme.colors.text,
    fontSize: 14,
    lineHeight: 20,
  },
  actions: {
    gap: theme.spacing.sm,
  },
});
