import { router, useFocusEffect } from "expo-router";
import { useCallback, useState } from "react";
import { Alert, FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { PrimaryButton } from "@/components/PrimaryButton";
import { localStorage } from "@/lib/storage";
import { supabase } from "@/lib/supabase";
import { Schedule } from "@/types/schedule";

export default function HomeScreen() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(false);

  const loadSchedules = useCallback(async () => {
    setLoading(true);
    const {
      data: { user }
    } = await supabase.auth.getUser();

    if (!user) {
      router.replace("/login");
      return;
    }

    const { data, error } = await supabase
      .from("schedules")
      .select("*")
      .eq("user_id", user.id)
      .order("created_at", { ascending: false });

    setLoading(false);

    if (error) {
      const cached = await localStorage.getSchedules();
      setSchedules(cached);
      Alert.alert("Showing offline schedules", error.message);
      return;
    }

    const nextSchedules = data ?? [];
    setSchedules(nextSchedules);
    await localStorage.saveSchedules(nextSchedules);
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadSchedules();
    }, [loadSchedules])
  );

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.replace("/login");
  }

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Schedules</Text>
          <Text style={styles.subtitle}>Your saved school and work weeks.</Text>
        </View>
        <Pressable onPress={handleSignOut}>
          <Text style={styles.signOut}>Sign out</Text>
        </Pressable>
      </View>

      <PrimaryButton title="New Schedule" onPress={() => router.push("/create-schedule")} />

      <FlatList
        data={schedules}
        refreshing={loading}
        onRefresh={loadSchedules}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No schedules yet. Create your first one.</Text>}
        renderItem={({ item }) => (
          <Pressable style={styles.scheduleCard} onPress={() => router.push(`/schedule/${item.id}`)}>
            <Text style={styles.scheduleTitle}>{item.title}</Text>
            <Text style={styles.scheduleMeta}>{item.semester || "No semester set"}</Text>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    padding: 20,
    paddingTop: 64
  },
  header: {
    alignItems: "flex-start",
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 18
  },
  title: {
    color: "#0f172a",
    fontSize: 34,
    fontWeight: "900"
  },
  subtitle: {
    color: "#64748b",
    fontSize: 15,
    marginTop: 4
  },
  signOut: {
    color: "#2563eb",
    fontWeight: "800",
    marginTop: 10
  },
  list: {
    gap: 12,
    paddingTop: 18
  },
  empty: {
    color: "#64748b",
    fontSize: 16,
    paddingTop: 28,
    textAlign: "center"
  },
  scheduleCard: {
    backgroundColor: "#ffffff",
    borderColor: "#e2e8f0",
    borderRadius: 14,
    borderWidth: 1,
    padding: 18
  },
  scheduleTitle: {
    color: "#0f172a",
    fontSize: 19,
    fontWeight: "800"
  },
  scheduleMeta: {
    color: "#64748b",
    fontSize: 14,
    marginTop: 6
  }
});
