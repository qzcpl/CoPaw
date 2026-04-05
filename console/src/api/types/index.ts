// 原有类型
export * from "./agent";
export * from "./agents";
export * from "./channel";
export * from "./heartbeat";
export * from "./chat";
export * from "./cronjob";
export * from "./env";
export * from "./mcp";
export * from "./provider";
export * from "./skill";
export * from "./workspace";
export * from "./tokenUsage";

// ✅ v4.0 新增：频道架构重构类型
export * from "./error";           // 错误类型和错误码
export * from "./callid";          // callId 管理类型
export * from "./bot";             // Bot 管理类型
export * from "./tenant";          // 租户管理类型
export * from "./auth";            // 认证类型
export * from "./identifiers";     // 六层标识体系（核心）
export * from "./monitor";         // 监控类型
export * from "./routing";         // 路由类型
export * from "./queue";           // 队列类型
export * from "./gray_release";    // 灰度发布类型

// Selective exports to avoid conflicts
export {
  type ChannelIdentifier,
  type CallerIdentifier,
  type CalledIdentifier,
  type SixLayerIdentifier,
  type IdentifierMappingStatus,
  type CallIdType,
} from "./identifiers";

export {
  type RoutingStrategy,
  type RoutingConfig,
  type FailoverConfig,
  type LoadBalancingConfig,
  type RoutingStrategyConfig,
  type RoutingStrategyCreateRequest,
  type RoutingStrategyUpdateRequest,
  type RoutingConfigCreateRequest,
  type RoutingConfigUpdateRequest,
  type RoutingDecision,
  type RoutingDecisionChain,
  type RoutingTestRequest,
  type RoutingTestResult,
  type RoutingTestOutput,
  type AgentRoutingStatus,
  type RoutingStatsResponse,
  type RoutingStatus,
  type RoutingRule,
  type RoutingListResponse,
  type MatchCondition,  // 匹配条件（用于灰度发布）
} from "./routing";

export {
  type UserProfile,
  type GroupContext,
  type SessionInfo,
  type SessionListResponse,
  type SessionContextV2,
  type BusMessageV3,
  type ContentType,
  type MessageDirection,
  type SendMessageRequest,
  type SendMessageResponse,
  type ChatSpec,
  type ChatHistory,
  type ChatDeleteResponse,
  type Session,
  type ChatStatus,
  type Message,
} from "./chat";

export {
  type SingleChannelConfig,
  type IMessageChannelConfig,
  type DiscordConfig,
  type DingTalkConfig,
  type FeishuConfig,
  type QQConfig,
  type ConsoleConfig,
  type TelegramConfig,
  type MQTTConfig,
  type MatrixConfig,
  type MattermostConfig,
  type WecomConfig,
  type VoiceChannelConfig,
  type XiaoYiConfig,
} from "./channel";

export {
  type GrayReleaseConfig,
  type GrayReleaseCreateRequest,
  type GrayReleaseUpdateRequest,
  type GrayReleaseMetrics,
  type GrayReleaseRule,
  type GrayReleaseHistory,
  type GrayReleaseListResponse,
  type GrayReleaseStatus,
} from "./gray_release";
