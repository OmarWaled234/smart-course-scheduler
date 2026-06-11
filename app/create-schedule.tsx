import { router } from "expo-router";
import { useState } from "react";
import { Alert, StyleSheet, Text, View } from "react-native";
import { FormInput } from "@/components/FormInput";
import { PrimaryButton } from "@/components/PrimaryButton";
import { supabase } from "@/lib/supabase";

export default function CreateScheduleScreen() {
  const [title, setTitle] = useState("");
  const [semester, setSemester] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleCreate() {
    const {
      data: { user }
    } = await supabase.auth.getUser();

    if (!user) {
      router.replace("/login");
      return;
    }

    setLoading(true);
    const { data, error } = await supabase
      .from("schedules")
      .insert({ title, semester, user_id: user.id })
      .select()
      .single();
    setLoading(false);

    if (error) {
      Alert.alert("Could not create schedule", error.message);
      return;
    }

    router.replace(`/schedule/${data.id}`);
  }

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>New Schedule</Text>
      <FormInput label="Title" value={title} onChangeText={setTitle} placeholder="Fall weekly plan" />
      <FormInput label="Semester" value={semester} onChangeText={setSemester} placeholder="Fall 2026" />
      <PrimaryButton title="Create Schedule" onPress={handleCreate} loading={loading} disabled={!title} />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    gap: 16,
    padding: 20,
    paddingTop: 28
  },
  title: {
    color: "#0f172a",
    fontSize: 30,
    fontWeight: "900",
    marginBottom: 4
  }
});
