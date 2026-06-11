import { Link, router } from "expo-router";
import { useState } from "react";
import { Alert, KeyboardAvoidingView, Platform, StyleSheet, Text, View } from "react-native";
import { FormInput } from "@/components/FormInput";
import { PrimaryButton } from "@/components/PrimaryButton";
import { supabase } from "@/lib/supabase";

export default function RegisterScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleRegister() {
    setLoading(true);
    const { error } = await supabase.auth.signUp({ email, password });
    setLoading(false);

    if (error) {
      Alert.alert("Could not register", error.message);
      return;
    }

    Alert.alert("Account created", "Check your email if confirmations are enabled.");
    router.replace("/home");
  }

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={styles.screen}>
      <View style={styles.card}>
        <Text style={styles.title}>Create Account</Text>
        <Text style={styles.subtitle}>Save schedules across devices with Supabase Auth.</Text>

        <FormInput label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" />
        <FormInput label="Password" value={password} onChangeText={setPassword} secureTextEntry />

        <PrimaryButton
          title="Register"
          onPress={handleRegister}
          loading={loading}
          disabled={!email || password.length < 6}
        />

        <Link href="/login" style={styles.link}>
          I already have an account
        </Link>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    justifyContent: "center",
    padding: 20
  },
  card: {
    gap: 16
  },
  title: {
    color: "#0f172a",
    fontSize: 32,
    fontWeight: "900"
  },
  subtitle: {
    color: "#64748b",
    fontSize: 16,
    lineHeight: 22,
    marginBottom: 8
  },
  link: {
    color: "#2563eb",
    fontSize: 16,
    fontWeight: "700",
    marginTop: 4,
    textAlign: "center"
  }
});
