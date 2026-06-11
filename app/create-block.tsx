import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import { Alert, ScrollView, StyleSheet, Text, View } from "react-native";
import { ColorPicker } from "@/components/ColorPicker";
import { FormInput } from "@/components/FormInput";
import { PrimaryButton } from "@/components/PrimaryButton";
import { supabase } from "@/lib/supabase";
import { timeOptions } from "@/lib/timeUtils";
import { DAYS, DayName } from "@/types/schedule";

export default function CreateBlockScreen() {
  const { scheduleId } = useLocalSearchParams<{ scheduleId: string }>();
  const [title, setTitle] = useState("");
  const [day, setDay] = useState<DayName>("Monday");
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("10:00");
  const [instructor, setInstructor] = useState("");
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const [color, setColor] = useState("#2563eb");
  const [loading, setLoading] = useState(false);

  async function handleSave() {
    if (!scheduleId) {
      Alert.alert("Missing schedule", "Open a schedule before adding a block.");
      return;
    }

    setLoading(true);
    const { error } = await supabase.from("schedule_blocks").insert({
      schedule_id: scheduleId,
      title,
      day,
      start_time: startTime,
      end_time: endTime,
      instructor,
      location,
      notes,
      color
    });
    setLoading(false);

    if (error) {
      Alert.alert("Could not save block", error.message);
      return;
    }

    router.back();
  }

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.title}>Add Block</Text>
      <FormInput label="Name" value={title} onChangeText={setTitle} placeholder="Calculus II" />

      <Text style={styles.label}>Day</Text>
      <View style={styles.chips}>
        {DAYS.map((item) => (
          <PrimaryButton
            key={item}
            title={item.slice(0, 3)}
            variant={day === item ? "primary" : "secondary"}
            onPress={() => setDay(item)}
            style={styles.chip}
          />
        ))}
      </View>

      <View style={styles.timeRow}>
        <FormInput label="Start" value={startTime} onChangeText={setStartTime} placeholder={timeOptions[4]} />
        <FormInput label="End" value={endTime} onChangeText={setEndTime} placeholder={timeOptions[6]} />
      </View>

      <FormInput label="Instructor or Manager" value={instructor} onChangeText={setInstructor} />
      <FormInput label="Location" value={location} onChangeText={setLocation} />
      <FormInput label="Notes" value={notes} onChangeText={setNotes} multiline style={styles.notes} />

      <Text style={styles.label}>Color</Text>
      <ColorPicker value={color} onChange={setColor} />

      <PrimaryButton title="Save Block" onPress={handleSave} loading={loading} disabled={!title} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    gap: 16,
    padding: 20,
    paddingBottom: 40
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
