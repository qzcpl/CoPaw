import { useState, useEffect } from "react";
import { useAppMessage } from "../../../hooks/useAppMessage";
import api from "../../../api";
import type { Session, SessionListResponse } from "./components/constants";
import { useAgentStore } from "../../../stores/agentStore";

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const { selectedAgent } = useAgentStore();
  const { message } = useAppMessage();

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const data: SessionListResponse = await api.listSessions();
      if (data && data.sessions) {
        setSessions(data.sessions as unknown as Session[]);
      }
    } catch (error) {
      console.error("❌ Failed to load sessions:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    const loadSessions = async () => {
      await fetchSessions();
    };

    if (mounted) {
      loadSessions();
    }

    return () => {
      mounted = false;
    };
  }, [selectedAgent]);

  const pauseSession = async (sessionId: string) => {
    try {
      await api.pauseSession(sessionId);
      setSessions(sessions.map((s) => (s.id === sessionId ? { ...s, status: "paused" as const } : s)));
      message.success("Paused successfully");
      return true;
    } catch (error) {
      console.error("❌ Failed to pause session:", error);
      message.error("Pause failed");
      return false;
    }
  };

  const resumeSession = async (sessionId: string) => {
    try {
      await api.resumeSession(sessionId);
      setSessions(sessions.map((s) => (s.id === sessionId ? { ...s, status: "active" as const } : s)));
      message.success("Resumed successfully");
      return true;
    } catch (error) {
      console.error("❌ Failed to resume session:", error);
      message.error("Resume failed");
      return false;
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      setSessions(sessions.filter((s) => s.id !== sessionId));
      message.success("Deleted successfully");
      return true;
    } catch (error) {
      console.error("❌ Failed to delete session:", error);
      message.error("Failed to delete");
      return false;
    }
  };

  return {
    sessions,
    loading,
    pauseSession,
    resumeSession,
    deleteSession,
  };
}
