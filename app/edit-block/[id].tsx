import { router, useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { Alert, ScrollView, StyleSheet, Text, View } from "react-native";
import { ColorPicker } from "@/components/ColorPicker";
import { FormInput } from "@/components/FormInput";
import { PrimaryButton } from "@/components/PrimaryButton";
import { supabase } from "@/lib/supabase";
import { DAYS, DayName, ScheduleBlock } from "@/types/schedule";

export default function EditBlockScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [block, setBlock] = useState<ScheduleBlock | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadBlock() {
      if (!id) {
        return;
      }

      const { data, error } = await supabase.from("schedule_blocks").select("*").eq("id", id).single();
      if (error) {
        Alert.alert("Could not load block", error.message);
        return;
      }
      setBlock(data);
    }

    loadBlock();
  }, [id]);

  function updateField<K extends keyof ScheduleBlock>(key: K, value: ScheduleBlock[K]) {
    setBlock((current) => (current ? { ...current, [key]: value } : current));
  }

  async function handleSave() {
    if (!block) {
      return;
    }

    setLoading(true);
    const { error } = await supabase
      .from("schedule_blocks")
      .update({
        title: block.title,
        day: block.day,
        start_time: block.start_time,
        end_time: block.end_time,
        instructor: block.instructor,
        location: block.location,
        notes: block.notes,
        color: block.color
      })
      .eq("id", block.id);
    setLoading(false);

    if (error) {
      Alert.alert("Could not update block", error.message);
      return;
    }

    router.back();
  }

  async function handleDelete() {
    if (!block) {
      return;
    }

    const { error } = await supabase.from("schedule_blocks").delete().eq("id", block.id);
    if (error) {
      Alert.alert("Could not delete block", error.message);
      return;
    }

    router.back();
  }

  if (!block) {
    return (
      <View style={styles.center}>
        <Text style={styles.label}>Loading block...</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.title}>Edit Block</Text>
      <FormInput label="Name" value={block.title} onChangeText={(value) => updateField("title", value)} />

      <Text style={styles.label}>Day</Text>
      <View style={styles.chips}>
        {DAYS.map((item) => (
          <PrimaryButton
            key={item}
            title={item.slice(0, 3)}
            variant={block.day === item ? "primary" : "secondary"}
            onPress={() => updateField("day", item as DayName)}
            style={styles.chip}
          />
        ))}
      </View>

      <View style={styles.timeRow}>
        <FormInput label="Start" value={block.start_time} onChangeText={(value) => updateField("start_time", value)} />
        <FormInput label="End" value={block.end_time} onChangeText={(value) => updateField("end_time", value)} />
      </View>

      <FormInput
        label="Instructor or Manager"
        value={block.instructor}
        onChangeText={(value) => updateField("instructor", value)}
      />
      <FormInput label="Location" value={block.location} onChangeText={(value) => updateField("location", value)} />
      <FormInput
        label="Notes"
        value={block.notes}
        onChangeText={(value) => updateField("notes", value)}
        multiline
        style={styles.notes}
      />

      <Text style={styles.label}>Color</Text>
      <ColorPicker value={block.color} onChange={(value) => updateField("color", value)} />

      <PrimaryButton title="Save Changes" onPress={handleSave} loading={loading} disabled={!block.title} />
      <PrimaryButton title="Delete Block" variant="danger" onPress={handleDelete} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    gap: 16,
    padding: 20,
    paddingBottom: 40
  },
  center: {
    alignItems: "center",
    flex: 1,
    justifyContent: "center"
  },
  title: {
    color: "#0f172a",
    fontSize: 30,
    fontWeight: "900"
  },
  label: {
    color: "#334155",
    fontSize: 14,
    fontWeight: "800"
  },
  chips: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8
  },
  chip: {
    minHeight: 42,
    minWidth: 64
  },
  timeRow: {
    flexDirection: "row",
    gap: 12
  },
  notes: {
    minHeight: 90,
    paddingTop: 12,
    textAlignVertical: "top"
  }
});
