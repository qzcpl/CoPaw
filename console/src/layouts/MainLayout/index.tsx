import { Layout } from "antd";
import { Routes, Route, useLocation, Navigate } from "react-router-dom";
import Sidebar from "../Sidebar";
import Header from "../Header";
import ConsoleCronBubble from "../../components/ConsoleCronBubble";
import styles from "../index.module.less";
import Chat from "../../pages/Chat";
import ChannelsPage from "../../pages/Control/Channels";
import SessionsPage from "../../pages/Control/Sessions";
import CronJobsPage from "../../pages/Control/CronJobs";
import HeartbeatPage from "../../pages/Control/Heartbeat";
import { CallIdManagement } from "../../pages/Control/CallIdManagement";
import { BotManagement } from "../../pages/Control/BotManagement";
import { TenantManagement } from "../../pages/Control/TenantManagement";
import { MonitorCenter } from "../../pages/Control/MonitorCenter";
import IntegrationTest from "../../pages/Control/IntegrationTest";
import RoutingManagement from "../../pages/Control/RoutingManagement";
import QueueManagement from "../../pages/Control/QueueManagement";
import { GrayReleaseManagement } from "../../pages/Control/GrayReleaseManagement";
import AgentConfigPage from "../../pages/Agent/Config";
import SkillsPage from "../../pages/Agent/Skills";
import SkillPoolPage from "../../pages/Agent/SkillPool";
import ToolsPage from "../../pages/Agent/Tools";
import WorkspacePage from "../../pages/Agent/Workspace";
import MCPPage from "../../pages/Agent/MCP";
import ModelsPage from "../../pages/Settings/Models";
import EnvironmentsPage from "../../pages/Settings/Environments";
import SecurityPage from "../../pages/Settings/Security";
import TokenUsagePage from "../../pages/Settings/TokenUsage";
import VoiceTranscriptionPage from "../../pages/Settings/VoiceTranscription";
import AgentsPage from "../../pages/Settings/Agents";

const { Content } = Layout;

const pathToKey: Record<string, string> = {
  "/chat": "chat",
  "/channels": "channels",
  "/sessions": "sessions",
  "/cron-jobs": "cron-jobs",
  "/heartbeat": "heartbeat",
  "/callid-management": "callid-management",
  "/bot-management": "bot-management",
  "/tenant-management": "tenant-management",
  "/monitor": "monitor",
  "/integration-test": "integration-test",
  "/routing-management": "routing-management",
  "/queue-management": "queue-management",
  "/gray-release": "gray-release",
  "/skills": "skills",
  "/skill-pool": "skill-pool",
  "/tools": "tools",
  "/mcp": "mcp",
  "/workspace": "workspace",
  "/agents": "agents",
  "/models": "models",
  "/environments": "environments",
  "/agent-config": "agent-config",
  "/security": "security",
  "/token-usage": "token-usage",
  "/voice-transcription": "voice-transcription",
};

export default function MainLayout() {
  const location = useLocation();
  const currentPath = location.pathname;
  const selectedKey = pathToKey[currentPath] || "chat";

  return (
    <Layout className={styles.mainLayout}>
      <Header />
      <Layout>
        <Sidebar selectedKey={selectedKey} />
        <Content className="page-container">
          <ConsoleCronBubble />
          <div className="page-content">
            <Routes>
              <Route path="/" element={<Navigate to="/chat" replace />} />
              <Route path="/chat/*" element={<Chat />} />
              <Route path="/channels" element={<ChannelsPage />} />
              <Route path="/sessions" element={<SessionsPage />} />
              <Route path="/cron-jobs" element={<CronJobsPage />} />
              <Route path="/heartbeat" element={<HeartbeatPage />} />
              <Route path="/skills" element={<SkillsPage />} />
              <Route path="/skill-pool" element={<SkillPoolPage />} />
              <Route path="/tools" element={<ToolsPage />} />
              <Route path="/mcp" element={<MCPPage />} />
              <Route path="/workspace" element={<WorkspacePage />} />
              <Route path="/agents" element={<AgentsPage />} />
              <Route path="/models" element={<ModelsPage />} />
              <Route path="/environments" element={<EnvironmentsPage />} />
              <Route path="/agent-config" element={<AgentConfigPage />} />
              <Route path="/security" element={<SecurityPage />} />
              <Route path="/token-usage" element={<TokenUsagePage />} />
              <Route
                path="/voice-transcription"
                element={<VoiceTranscriptionPage />}
              />
              {/* 新增管理页面 */}
              <Route path="/callid-management" element={<CallIdManagement />} />
              <Route path="/bot-management" element={<BotManagement />} />
              <Route path="/tenant-management" element={<TenantManagement />} />
              <Route path="/monitor" element={<MonitorCenter />} />
              <Route path="/integration-test" element={<IntegrationTest />} />
              <Route path="/routing-management" element={<RoutingManagement />} />
              <Route path="/queue-management" element={<QueueManagement />} />
              <Route path="/gray-release" element={<GrayReleaseManagement />} />
            </Routes>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}
