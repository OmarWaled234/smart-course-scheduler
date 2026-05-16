import { Ionicons } from "@expo/vector-icons";
import { StatusBar } from "expo-status-bar";
import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View
} from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

import {
  API_BASE_URL,
  Course,
  Dashboard,
  ScheduleSession,
  StudyBlock,
  Task,
  api
} from "./src/api";

type Tab = "Home" | "Tasks" | "Courses" | "Blocks" | "Schedule";

const TABS: { name: Tab; icon: keyof typeof Ionicons.glyphMap }[] = [
  { name: "Home", icon: "grid-outline" },
  { name: "Tasks", icon: "checkbox-outline" },
  { name: "Courses", icon: "library-outline" },
  { name: "Blocks", icon: "time-outline" },
  { name: "Schedule", icon: "calendar-outline" }
];

const taskTypes = ["assignment", "exam", "quiz", "project", "reading", "other"];
const priorities = ["low", "medium", "high"];
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const emptyDashboard: Dashboard = {
  total_tasks: 0,
  completed_tasks: 0,
  overdue_tasks: 0,
  upcoming_tasks: 0,
  remaining_hours: 0,
  study_blocks: 0,
  tasks_by_course: [],
  hours_by_course: []
};

export default function App() {
  const [tab, setTab] = useState<Tab>("Home");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [dashboard, setDashboard] = useState<Dashboard>(emptyDashboard);
  const [courses, setCourses] = useState<Course[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [blocks, setBlocks] = useState<StudyBlock[]>([]);
  const [schedule, setSchedule] = useState<ScheduleSession[]>([]);
  const [modal, setModal] = useState<"course" | "task" | "block" | null>(null);

  const loadData = useCallback(async () => {
    setRefreshing(true);
    setError("");
    try {
      const [nextDashboard, nextCourses, nextTasks, nextBlocks, nextSchedule] = await Promise.all([
        api.dashboard(),
        api.courses(),
        api.tasks(),
        api.studyBlocks(),
        api.schedule()
      ]);
      setDashboard(nextDashboard);
      setCourses(nextCourses);
      setTasks(nextTasks);
      setBlocks(nextBlocks);
      setSchedule(nextSchedule);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load scheduler data.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const todayPlan = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    return schedule.filter((item) => item.date === today);
  }, [schedule]);

  const nextTasks = useMemo(
    () => tasks.filter((task) => !task.completed).slice(0, 4),
    [tasks]
  );

  const runAction = async (action: () => Promise<unknown>) => {
    try {
      await action();
      await loadData();
    } catch (err) {
      Alert.alert("Action failed", err instanceof Error ? err.message : "Please try again.");
    }
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar style="dark" />
        <View style={styles.header}>
          <View>
            <Text style={styles.kicker}>Smart Course Scheduler</Text>
            <Text style={styles.title}>{tab}</Text>
          </View>
          <Pressable
            accessibilityLabel="Refresh"
            style={styles.iconButton}
            onPress={loadData}
            disabled={refreshing}
          >
            {refreshing ? (
              <ActivityIndicator size="small" color="#0F766E" />
            ) : (
              <Ionicons name="refresh" size={20} color="#12343B" />
            )}
          </Pressable>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#0F766E" />
            <Text style={styles.muted}>Connecting to {API_BASE_URL}</Text>
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
            {error ? (
              <View style={styles.errorBox}>
                <Text style={styles.errorTitle}>Backend unavailable</Text>
                <Text style={styles.errorText}>{error}</Text>
                <Text style={styles.errorHint}>Run: uvicorn api:app --reload --host 0.0.0.0</Text>
              </View>
            ) : null}

            {tab === "Home" ? (
              <HomeScreen
                dashboard={dashboard}
                todayPlan={todayPlan}
                nextTasks={nextTasks}
                onDemo={() => runAction(api.demoData)}
              />
            ) : null}
            {tab === "Tasks" ? (
              <TasksScreen
                courses={courses}
                tasks={tasks}
                onAdd={() => setModal("task")}
                onComplete={(task) => runAction(() => api.completeTask(task.id, !task.completed))}
                onDelete={(task) => runAction(() => api.deleteTask(task.id))}
              />
            ) : null}
            {tab === "Courses" ? (
              <CoursesScreen
                courses={courses}
                onAdd={() => setModal("course")}
                onDelete={(course) => runAction(() => api.deleteCourse(course.id))}
              />
            ) : null}
            {tab === "Blocks" ? (
              <BlocksScreen
                blocks={blocks}
                onAdd={() => setModal("block")}
                onComplete={(block) => runAction(() => api.completeStudyBlock(block.id, !block.completed))}
                onDelete={(block) => runAction(() => api.deleteStudyBlock(block.id))}
              />
            ) : null}
            {tab === "Schedule" ? <ScheduleScreen schedule={schedule} /> : null}
          </ScrollView>
        )}

        <View style={styles.tabBar}>
          {TABS.map((item) => {
            const active = tab === item.name;
            return (
              <Pressable key={item.name} style={styles.tabItem} onPress={() => setTab(item.name)}>
                <Ionicons name={item.icon} size={21} color={active ? "#0F766E" : "#667085"} />
                <Text style={[styles.tabText, active && styles.tabTextActive]}>{item.name}</Text>
              </Pressable>
            );
          })}
        </View>

        <CourseModal
          visible={modal === "course"}
          onClose={() => setModal(null)}
          onSave={(payload) =>
            runAction(async () => {
              await api.createCourse(payload);
              setModal(null);
            })
          }
        />
        <TaskModal
          visible={modal === "task"}
          courses={courses}
          onClose={() => setModal(null)}
          onSave={(payload) =>
            runAction(async () => {
              await api.createTask(payload);
              setModal(null);
            })
          }
        />
        <BlockModal
          visible={modal === "block"}
          onClose={() => setModal(null)}
          onSave={(payload) =>
            runAction(async () => {
              await api.createStudyBlock(payload);
              setModal(null);
            })
          }
        />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

function HomeScreen({
  dashboard,
  todayPlan,
  nextTasks,
  onDemo
}: {
  dashboard: Dashboard;
  todayPlan: ScheduleSession[];
  nextTasks: Task[];
  onDemo: () => void;
}) {
  return (
    <View style={styles.stack}>
      <View style={styles.metricsGrid}>
        <Metric label="Tasks" value={dashboard.total_tasks} tone="#0F766E" />
        <Metric label="Done" value={dashboard.completed_tasks} tone="#2563EB" />
        <Metric label="Overdue" value={dashboard.overdue_tasks} tone="#DC2626" />
        <Metric label="Hours left" value={dashboard.remaining_hours} tone="#7C3AED" />
      </View>

      <Section title="Today">
        {todayPlan.length ? (
          todayPlan.map((item, index) => <ScheduleCard key={`${item.task}-${index}`} item={item} />)
        ) : (
          <EmptyState icon="today-outline" text="No generated sessions for today." />
        )}
      </Section>

      <Section title="Next Up">
        {nextTasks.length ? (
          nextTasks.map((task) => <TaskCard key={task.id} task={task} />)
        ) : (
          <EmptyState icon="sparkles-outline" text="No unfinished tasks yet." />
        )}
      </Section>

      <Pressable style={styles.primaryButton} onPress={onDemo}>
        <Ionicons name="flask-outline" size={18} color="#FFFFFF" />
        <Text style={styles.primaryButtonText}>Load Demo Data</Text>
      </Pressable>
    </View>
  );
}

function TasksScreen({
  courses,
  tasks,
  onAdd,
  onComplete,
  onDelete
}: {
  courses: Course[];
  tasks: Task[];
  onAdd: () => void;
  onComplete: (task: Task) => void;
  onDelete: (task: Task) => void;
}) {
  return (
    <View style={styles.stack}>
      <AddButton label="Add Task" disabled={!courses.length} onPress={onAdd} />
      {!courses.length ? <EmptyState icon="library-outline" text="Add a course before creating tasks." /> : null}
      {tasks.length ? (
        tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            actions={
              <CardActions
                complete={Boolean(task.completed)}
                onComplete={() => onComplete(task)}
                onDelete={() => onDelete(task)}
              />
            }
          />
        ))
      ) : (
        <EmptyState icon="checkbox-outline" text="No tasks yet." />
      )}
    </View>
  );
}

function CoursesScreen({
  courses,
  onAdd,
  onDelete
}: {
  courses: Course[];
  onAdd: () => void;
  onDelete: (course: Course) => void;
}) {
  return (
    <View style={styles.stack}>
      <AddButton label="Add Course" onPress={onAdd} />
      {courses.length ? (
        courses.map((course) => (
          <View key={course.id} style={styles.card}>
            <View style={styles.row}>
              <View style={[styles.swatch, { backgroundColor: course.color }]} />
              <View style={styles.flex}>
                <Text style={styles.cardTitle}>{course.name}</Text>
                <Text style={styles.muted}>{course.instructor || "No instructor"}</Text>
              </View>
              <IconAction icon="trash-outline" onPress={() => onDelete(course)} />
            </View>
          </View>
        ))
      ) : (
        <EmptyState icon="library-outline" text="No courses yet." />
      )}
    </View>
  );
}

function BlocksScreen({
  blocks,
  onAdd,
  onComplete,
  onDelete
}: {
  blocks: StudyBlock[];
  onAdd: () => void;
  onComplete: (block: StudyBlock) => void;
  onDelete: (block: StudyBlock) => void;
}) {
  return (
    <View style={styles.stack}>
      <AddButton label="Add Study Block" onPress={onAdd} />
      {blocks.length ? (
        blocks.map((block) => (
          <View key={block.id} style={styles.card}>
            <View style={styles.row}>
              <View style={styles.flex}>
                <Text style={styles.cardTitle}>{block.day_of_week}</Text>
                <Text style={styles.muted}>
                  {block.start_time} - {block.end_time} • {block.duration_hours}h
                </Text>
              </View>
              <CardActions
                complete={Boolean(block.completed)}
                onComplete={() => onComplete(block)}
                onDelete={() => onDelete(block)}
              />
            </View>
          </View>
        ))
      ) : (
        <EmptyState icon="time-outline" text="No study blocks yet." />
      )}
    </View>
  );
}

function ScheduleScreen({ schedule }: { schedule: ScheduleSession[] }) {
  return (
    <View style={styles.stack}>
      {schedule.length ? (
        schedule.map((item, index) => <ScheduleCard key={`${item.date}-${item.start_time}-${index}`} item={item} />)
      ) : (
        <EmptyState icon="calendar-outline" text="Add unfinished tasks and open blocks to generate a plan." />
      )}
    </View>
  );
}

function CourseModal({
  visible,
  onClose,
  onSave
}: {
  visible: boolean;
  onClose: () => void;
  onSave: (payload: Omit<Course, "id">) => void;
}) {
  const [name, setName] = useState("");
  const [instructor, setInstructor] = useState("");
  const [color, setColor] = useState("#4C78A8");

  const save = () => {
    if (!name.trim()) {
      Alert.alert("Course name required");
      return;
    }
    onSave({ name, instructor, color });
    setName("");
    setInstructor("");
    setColor("#4C78A8");
  };

  return (
    <FormModal title="Add Course" visible={visible} onClose={onClose} onSave={save}>
      <Field label="Name" value={name} onChangeText={setName} placeholder="Biology" />
      <Field label="Instructor" value={instructor} onChangeText={setInstructor} placeholder="Dr. Patel" />
      <Field label="Color" value={color} onChangeText={setColor} placeholder="#4C78A8" />
    </FormModal>
  );
}

function TaskModal({
  visible,
  courses,
  onClose,
  onSave
}: {
  visible: boolean;
  courses: Course[];
  onClose: () => void;
  onSave: Parameters<typeof api.createTask>[0] extends infer T ? (payload: T) => void : never;
}) {
  const [title, setTitle] = useState("");
  const [courseId, setCourseId] = useState<number | null>(courses[0]?.id ?? null);
  const [taskType, setTaskType] = useState("assignment");
  const [dueDate, setDueDate] = useState(new Date().toISOString().slice(0, 10));
  const [hours, setHours] = useState("1.5");
  const [priority, setPriority] = useState("medium");

  useEffect(() => {
    if (!courseId && courses[0]) {
      setCourseId(courses[0].id);
    }
  }, [courseId, courses]);

  const save = () => {
    const estimated = Number(hours);
    if (!title.trim() || !courseId || !estimated) {
      Alert.alert("Task needs a title, course, and hours.");
      return;
    }
    onSave({
      title,
      course_id: courseId,
      task_type: taskType,
      due_date: dueDate,
      estimated_hours: estimated,
      completed_hours: 0,
      priority,
      completed: false
    });
    setTitle("");
    setHours("1.5");
  };

  return (
    <FormModal title="Add Task" visible={visible} onClose={onClose} onSave={save}>
      <Field label="Title" value={title} onChangeText={setTitle} placeholder="Chapter quiz" />
      <ChipPicker
        label="Course"
        options={courses.map((course) => ({ label: course.name, value: String(course.id) }))}
        value={String(courseId ?? "")}
        onChange={(value) => setCourseId(Number(value))}
      />
      <ChipPicker label="Type" options={taskTypes.map(toOption)} value={taskType} onChange={setTaskType} />
      <Field label="Due Date" value={dueDate} onChangeText={setDueDate} placeholder="2026-05-20" />
      <Field label="Estimated Hours" value={hours} onChangeText={setHours} keyboardType="decimal-pad" />
      <ChipPicker label="Priority" options={priorities.map(toOption)} value={priority} onChange={setPriority} />
    </FormModal>
  );
}

function BlockModal({
  visible,
  onClose,
  onSave
}: {
  visible: boolean;
  onClose: () => void;
  onSave: Parameters<typeof api.createStudyBlock>[0] extends infer T ? (payload: T) => void : never;
}) {
  const [day, setDay] = useState("Monday");
  const [start, setStart] = useState("16:00");
  const [end, setEnd] = useState("18:00");

  const save = () => {
    onSave({ day_of_week: day, start_time: start, end_time: end, completed: false });
  };

  return (
    <FormModal title="Add Study Block" visible={visible} onClose={onClose} onSave={save}>
      <ChipPicker label="Day" options={days.map(toOption)} value={day} onChange={setDay} />
      <Field label="Start" value={start} onChangeText={setStart} placeholder="16:00" />
      <Field label="End" value={end} onChangeText={setEnd} placeholder="18:00" />
    </FormModal>
  );
}

function FormModal({
  title,
  visible,
  children,
  onClose,
  onSave
}: {
  title: string;
  visible: boolean;
  children: React.ReactNode;
  onClose: () => void;
  onSave: () => void;
}) {
  return (
    <Modal visible={visible} animationType="slide" transparent>
      <View style={styles.modalBackdrop}>
        <View style={styles.modalPanel}>
          <View style={styles.row}>
            <Text style={styles.modalTitle}>{title}</Text>
            <IconAction icon="close" onPress={onClose} />
          </View>
          {children}
          <Pressable style={styles.primaryButton} onPress={onSave}>
            <Ionicons name="save-outline" size={18} color="#FFFFFF" />
            <Text style={styles.primaryButtonText}>Save</Text>
          </Pressable>
        </View>
      </View>
    </Modal>
  );
}

function Metric({ label, value, tone }: { label: string; value: number; tone: string }) {
  return (
    <View style={styles.metric}>
      <Text style={[styles.metricValue, { color: tone }]}>{value}</Text>
      <Text style={styles.metricLabel}>{label}</Text>
    </View>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}

function TaskCard({ task, actions }: { task: Task; actions?: React.ReactNode }) {
  return (
    <View style={[styles.card, task.is_overdue && styles.overdueCard]}>
      <View style={styles.row}>
        <View style={[styles.swatch, { backgroundColor: task.course_color || "#0F766E" }]} />
        <View style={styles.flex}>
          <Text style={styles.cardTitle}>{task.title}</Text>
          <Text style={styles.muted}>
            {task.course_name} • {task.task_type} • due {task.due_date}
          </Text>
          <Text style={styles.progressText}>
            {task.completed_hours}/{task.estimated_hours}h • {task.priority}
          </Text>
        </View>
        {actions}
      </View>
    </View>
  );
}

function ScheduleCard({ item }: { item: ScheduleSession }) {
  return (
    <View style={[styles.card, item.overdue && styles.overdueCard]}>
      <View style={styles.row}>
        <View style={styles.datePill}>
          <Text style={styles.dateDay}>{item.day.slice(0, 3)}</Text>
          <Text style={styles.dateTime}>{item.start_time}</Text>
        </View>
        <View style={styles.flex}>
          <Text style={styles.cardTitle}>{item.task}</Text>
          <Text style={styles.muted}>
            {item.course} • {item.session_hours}h • {item.start_time}-{item.end_time}
          </Text>
        </View>
      </View>
    </View>
  );
}

function AddButton({ label, onPress, disabled = false }: { label: string; onPress: () => void; disabled?: boolean }) {
  return (
    <Pressable style={[styles.primaryButton, disabled && styles.disabled]} onPress={onPress} disabled={disabled}>
      <Ionicons name="add" size={20} color="#FFFFFF" />
      <Text style={styles.primaryButtonText}>{label}</Text>
    </Pressable>
  );
}

function CardActions({
  complete,
  onComplete,
  onDelete
}: {
  complete: boolean;
  onComplete: () => void;
  onDelete: () => void;
}) {
  return (
    <View style={styles.actions}>
      <IconAction icon={complete ? "radio-button-off-outline" : "checkmark-circle-outline"} onPress={onComplete} />
      <IconAction icon="trash-outline" onPress={onDelete} />
    </View>
  );
}

function IconAction({ icon, onPress }: { icon: keyof typeof Ionicons.glyphMap; onPress: () => void }) {
  return (
    <Pressable style={styles.smallIconButton} onPress={onPress}>
      <Ionicons name={icon} size={18} color="#12343B" />
    </Pressable>
  );
}

function Field({
  label,
  value,
  onChangeText,
  placeholder,
  keyboardType = "default"
}: {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  placeholder?: string;
  keyboardType?: "default" | "decimal-pad";
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        keyboardType={keyboardType}
        placeholderTextColor="#98A2B3"
      />
    </View>
  );
}

function ChipPicker({
  label,
  options,
  value,
  onChange
}: {
  label: string;
  options: { label: string; value: string }[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <View style={styles.chips}>
        {options.map((option) => {
          const active = option.value === value;
          return (
            <Pressable
              key={option.value}
              style={[styles.chip, active && styles.chipActive]}
              onPress={() => onChange(option.value)}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>{option.label}</Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

function EmptyState({ icon, text }: { icon: keyof typeof Ionicons.glyphMap; text: string }) {
  return (
    <View style={styles.empty}>
      <Ionicons name={icon} size={26} color="#667085" />
      <Text style={styles.emptyText}>{text}</Text>
    </View>
  );
}

function toOption(value: string) {
  return { label: value, value };
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#F7F9FC"
  },
  header: {
    minHeight: 78,
    paddingHorizontal: 20,
    paddingVertical: 12,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottomWidth: 1,
    borderBottomColor: "#D8E0EA",
    backgroundColor: "#FFFFFF"
  },
  kicker: {
    fontSize: 12,
    color: "#667085",
    fontWeight: "700",
    textTransform: "uppercase"
  },
  title: {
    fontSize: 28,
    color: "#12343B",
    fontWeight: "800"
  },
  iconButton: {
    width: 42,
    height: 42,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#EAF4F4"
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12
  },
  content: {
    padding: 16,
    paddingBottom: 94
  },
  stack: {
    gap: 14
  },
  errorBox: {
    padding: 14,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#FECACA",
    backgroundColor: "#FEF2F2",
    marginBottom: 12
  },
  errorTitle: {
    color: "#991B1B",
    fontWeight: "800",
    fontSize: 15
  },
  errorText: {
    color: "#7F1D1D",
    marginTop: 5
  },
  errorHint: {
    color: "#7F1D1D",
    marginTop: 8,
    fontFamily: "monospace"
  },
  metricsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10
  },
  metric: {
    width: "48%",
    minHeight: 92,
    backgroundColor: "#FFFFFF",
    borderRadius: 8,
    padding: 14,
    borderWidth: 1,
    borderColor: "#D8E0EA",
    justifyContent: "center"
  },
  metricValue: {
    fontSize: 27,
    fontWeight: "800"
  },
  metricLabel: {
    color: "#667085",
    marginTop: 4,
    fontWeight: "600"
  },
  section: {
    gap: 10
  },
  sectionTitle: {
    color: "#12343B",
    fontSize: 18,
    fontWeight: "800"
  },
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 8,
    padding: 14,
    borderWidth: 1,
    borderColor: "#D8E0EA"
  },
  overdueCard: {
    borderColor: "#FCA5A5",
    backgroundColor: "#FFF7F7"
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12
  },
  flex: {
    flex: 1
  },
  swatch: {
    width: 12,
    height: 44,
    borderRadius: 4
  },
  cardTitle: {
    color: "#12343B",
    fontSize: 16,
    fontWeight: "800"
  },
  muted: {
    color: "#667085",
    marginTop: 3
  },
  progressText: {
    color: "#0F766E",
    marginTop: 7,
    fontWeight: "700"
  },
  datePill: {
    width: 68,
    minHeight: 56,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#EAF4F4"
  },
  dateDay: {
    color: "#0F766E",
    fontWeight: "800"
  },
  dateTime: {
    color: "#12343B",
    fontWeight: "700",
    marginTop: 2
  },
  primaryButton: {
    minHeight: 48,
    borderRadius: 8,
    backgroundColor: "#0F766E",
    alignItems: "center",
    justifyContent: "center",
    flexDirection: "row",
    gap: 8,
    paddingHorizontal: 14
  },
  primaryButtonText: {
    color: "#FFFFFF",
    fontWeight: "800"
  },
  disabled: {
    opacity: 0.45
  },
  actions: {
    flexDirection: "row",
    gap: 8
  },
  smallIconButton: {
    width: 36,
    height: 36,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#F1F5F9"
  },
  empty: {
    minHeight: 112,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#D8E0EA",
    borderStyle: "dashed",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    padding: 18
  },
  emptyText: {
    color: "#667085",
    textAlign: "center",
    fontWeight: "600"
  },
  modalBackdrop: {
    flex: 1,
    justifyContent: "flex-end",
    backgroundColor: "rgba(18, 52, 59, 0.34)"
  },
  modalPanel: {
    backgroundColor: "#FFFFFF",
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    padding: 20,
    gap: 14,
    maxHeight: "86%"
  },
  modalTitle: {
    flex: 1,
    color: "#12343B",
    fontSize: 21,
    fontWeight: "800"
  },
  field: {
    gap: 8
  },
  fieldLabel: {
    color: "#344054",
    fontWeight: "800"
  },
  input: {
    minHeight: 46,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#D8E0EA",
    paddingHorizontal: 12,
    color: "#12343B",
    backgroundColor: "#FFFFFF"
  },
  chips: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8
  },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 9,
    borderRadius: 8,
    backgroundColor: "#F1F5F9",
    borderWidth: 1,
    borderColor: "#E4E7EC"
  },
  chipActive: {
    backgroundColor: "#0F766E",
    borderColor: "#0F766E"
  },
  chipText: {
    color: "#344054",
    fontWeight: "700"
  },
  chipTextActive: {
    color: "#FFFFFF"
  },
  tabBar: {
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 0,
    minHeight: 74,
    paddingHorizontal: 8,
    paddingTop: 8,
    paddingBottom: 12,
    flexDirection: "row",
    backgroundColor: "#FFFFFF",
    borderTopWidth: 1,
    borderTopColor: "#D8E0EA"
  },
  tabItem: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 4
  },
  tabText: {
    fontSize: 11,
    color: "#667085",
    fontWeight: "700"
  },
  tabTextActive: {
    color: "#0F766E"
  }
});
