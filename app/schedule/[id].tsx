import { router, useFocusEffect, useLocalSearchParams } from "expo-router";
import { useCallback, useState } from "react";
import { Alert, StyleSheet, Text, View } from "react-native";
import { CalendarGrid } from "@/components/CalendarGrid";
import { PrimaryButton } from "@/components/PrimaryButton";
import { localStorage } from "@/lib/storage";
import { supabase } from "@/lib/supabase";
import { Schedule, ScheduleBlock } from "@/types/schedule";

export default function ScheduleScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [blocks, setBlocks] = useState<ScheduleBlock[]>([]);

  const loadSchedule = useCallback(async () => {
    if (!id) {
      return;
    }

    const [scheduleResult, blocksResult] = await Promise.all([
      supabase.from("schedules").select("*").eq("id", id).single(),
      supabase.from("schedule_blocks").select("*").eq("schedule_id", id).order("start_time")
    ]);

    if (scheduleResult.error || blocksResult.error) {
      const [cachedSchedules, cachedBlocks] = await Promise.all([
        localStorage.getSchedules(),
        localStorage.getBlocks()
      ]);
      setSchedule(cachedSchedules.find((item) => item.id === id) ?? null);
      setBlocks(cachedBlocks.filter((block) => block.schedule_id === id));
      Alert.alert("Showing offline copy", scheduleResult.error?.message ?? blocksResult.error?.message);
      return;
    }

    setSchedule(scheduleResult.data);
    setBlocks(blocksResult.data ?? []);
    await localStorage.saveBlocks(blocksResult.data ?? []);
  }, [id]);

  useFocusEffect(
    useCallback(() => {
      loadSchedule();
    }, [loadSchedule])
  );

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text numberOfLines={1} style={styles.title}>
            {schedule?.title ?? "Schedule"}
          </Text>
          <Text style={styles.subtitle}>{schedule?.semester ?? "Weekly calendar"}</Text>
        </View>
        <PrimaryButton title="Add" onPress={() => router.push({ pathname: "/create-block", params: { scheduleId: id } })} />
      </View>

      <CalendarGrid blocks={blocks} onBlockPress={(block) => router.push(`/edit-block/${block.id}`)} />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    paddingTop: 18
  },
  header: {
    alignItems: "center",
    flexDirection: "row",
    gap: 12,
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingBottom: 16
  },
  headerText: {
    flex: 1
  },
  title: {
    color: "#0f172a",
    fontSize: 28,
    fontWeight: "900"
  },
  subtitle: {
    color: "#64748b",
    fontSize: 14,
    marginTop: 3
  }
});
