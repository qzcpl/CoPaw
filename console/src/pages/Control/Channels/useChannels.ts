import { useState, useEffect, useCallback, useMemo } from "react";
import api from "../../../api";
import { useAgentStore } from "../../../stores/agentStore";
import type { ChannelConfig } from "../../../api/types";

export function useChannels() {
  const { selectedAgent } = useAgentStore();
  const [channels, setChannels] = useState<
    Record<string, Record<string, unknown>>
  >({});
  const [channelTypes, setChannelTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchChannels = useCallback(async () => {
    setLoading(true);
    try {
      const [data, types] = await Promise.all([
        api.listChannels(),
        api.listChannelTypes(),
      ]);
      
      // 适配新 API 格式：数组 → 对象
      let channelsMap: Record<string, Record<string, unknown>> = {};
      if (Array.isArray(data)) {
        // 新格式：[{ channel_id, config, status, ... }, ...]
        channelsMap = (data as ChannelConfig[]).reduce((acc, channel) => {
          acc[channel.channel_id] = {
            ...channel.config,
            status: channel.status,
            created_at: channel.created_at,
            updated_at: channel.updated_at,
            tenant_id: channel.tenant_id,
          };
          return acc;
        }, {} as Record<string, Record<string, unknown>>);
      } else if (data && typeof data === 'object') {
        // 旧格式：{ console: {...}, dingtalk: {...} }
        channelsMap = data as Record<string, Record<string, unknown>>;
      }
      
      setChannels(channelsMap);
      if (types) setChannelTypes(types);
    } catch (error) {
      console.error("❌ Failed to load channels:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChannels();
  }, [fetchChannels, selectedAgent]);

  // Built-in channels come first (in a fixed order), then custom channels
  const builtinOrder = useMemo(
    () => [
      "console",
      "dingtalk",
      "feishu",
      "imessage",
      "discord",
      "telegram",
      "qq",
      "matrix",
      "xiaoyi",
    ],
    [],
  );

  const orderedKeys = useMemo(
    () => [
      ...builtinOrder.filter((k) => channelTypes.includes(k)),
      ...channelTypes.filter((k) => !builtinOrder.includes(k)),
    ],
    [builtinOrder, channelTypes],
  );

  // Read isBuiltin from API response
  const isBuiltin = useCallback(
    (key: string) => Boolean(channels[key]?.isBuiltin),
    [channels],
  );

  return {
    channels,
    channelTypes,
    orderedKeys,
    isBuiltin,
    loading,
    fetchChannels,
  };
}
