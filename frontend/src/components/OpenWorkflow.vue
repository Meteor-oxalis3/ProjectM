<script lang="ts" setup>
import { Position, VueFlow, Panel } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { MiniMap } from '@vue-flow/minimap';
import { Controls } from '@vue-flow/controls';
import dagre from '@dagrejs/dagre';
import { ref, watch, onBeforeUnmount } from 'vue';
import { countObjects } from '@/utils/vueflow';
import { applyStyles } from '@/utils/dagDarkMode';
import CompleteNode from '@/components/CompleteNode.vue';
import LoadingNode from '@/components/LoadingNode.vue';
import WaitingNode from '@/components/WaitingNode.vue';

const nodeTypes: any = {
  complete: CompleteNode,
  loading: LoadingNode,
  waiting: WaitingNode
};

import '@vue-flow/controls/dist/style.css';
import '@vue-flow/minimap/dist/style.css'
import axios from 'axios';
import Workflow from '@/pages/workflow.vue';

const props = defineProps<{ workflowUuid: string }>();

const g = new dagre.graphlib.Graph();
g.setGraph({
  rankdir: 'LR',
  nodesep: 80,
  edgesep: 10,
  ranksep: 30,
});
g.setDefaultEdgeLabel(() => ({}));

const inputData = ref<any>(null);
const nodes = ref<any[]>([]);
const edges = ref<any[]>([]);
const isDarkMode = ref(false);
const ErrDialog = ref(false);
const errorMessage = ref('当前流程未能正常运行，请删除本流程。');

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value;
  applyStyles(isDarkMode);
};

const isWorkflowLoading = ref(false);
const emit = defineEmits(['updateWorkflowDialog']); // 定义一个事件

const fetchData = async (workflowUuid: string) => {
  try {
    isWorkflowLoading.value = true;
    errorMessage.value = '当前流程未能正常运行，请删除本流程。';
    const response = await axios.post('/api/workflow_data', {
      workflow_uuid: workflowUuid
    });

    inputData.value = await response.data;

    if (inputData.value.error || !inputData.value.dag) {
      ErrDialog.value = true;
      errorMessage.value = inputData.value.error || '流程数据不完整';
      isWorkflowLoading.value = false;
      return;
    }

    inputData.value.dag.objects.forEach((node: any) => {
      node.label = node.label.replace(/\\n/g, ' for ');
    });

    const objectNum = countObjects(inputData.value);

    const graphNodes = inputData.value.dag.objects.map((node: any) => ({
      id: node.name,
      label: node.label,
      width: 250,
      height: 50,
    }));

    const graphEdges = inputData.value.dag.edges.map((edge: any) => ({
      source: edge.tail.toString(),
      target: edge.head.toString(),
    }));

    graphNodes.forEach((node: any) => {
      g.setNode(node.id, {
        label: node.label,
        width: node.width,
        height: node.height,
        style: node.style,
      });
    });

    graphEdges.forEach((edge: any) => {
      g.setEdge(edge.source, edge.target);
    });

    dagre.layout(g);

    nodes.value = g.nodes().map((nodeId) => {
      const node = g.node(nodeId);
      const nodeStatus = getNodeStatus(nodeId, inputData.value);
      return {
        id: nodeId,
        type: nodeStatus,
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        position: { x: node.x, y: node.y },
        data: { label: node.label },
        // style: node.style,
      };
    });

    edges.value = g.edges().map((edgeObj) => ({
      id: `e${edgeObj.v}->${edgeObj.w}`,
      source: edgeObj.v,
      target: edgeObj.w,
    }));

  } catch (error) {
    console.error(error);
    ErrDialog.value = true;
  } finally {
    isWorkflowLoading.value = false;
  }
};

const getNodeStatus = (nodeId: string, data: any) => {
  const completedNodes = data.completed.split(',').map((id: string) => id.trim());
  const ongoingNodes = data.ongoing.split(',').map((id: string) => id.trim());
  const unfinishedNodes = data.unfinished.split(',').map((id: string) => id.trim());

  if (completedNodes.includes(nodeId)) {
    return 'complete';
  } else if (ongoingNodes.includes(nodeId)) {
    return 'loading';
  } else if (unfinishedNodes.includes(nodeId)) {
    return 'waiting';
  } else {
    return 'default';
  }
};

let autoRefreshTimer: ReturnType<typeof setInterval> | null = null;

watch(() => props.workflowUuid, (newUuid) => {
  if (autoRefreshTimer) { clearInterval(autoRefreshTimer); autoRefreshTimer = null; }
  if (newUuid) {
    fetchData(newUuid);
    autoRefreshTimer = setInterval(() => fetchData(newUuid), 60000);
  }
}, { immediate: true });

onBeforeUnmount(() => {
  if (autoRefreshTimer) { clearInterval(autoRefreshTimer); autoRefreshTimer = null; }
});
</script>

<template>
      <v-progress-circular
      v-if="isWorkflowLoading"
      indeterminate
      color="primary"
      class="loading-indicator"
      size="64"
    />
  <VueFlow
    :nodes="nodes"
    :edges="edges"
    :node-types="nodeTypes"
    fit-view-on-init
    snap-to-grid
    :class="{ 'dark-mode': isDarkMode }"
  >
    <!-- 背景 -->
    <Background />
    <!-- 控制器 -->
    <Panel class="process-panel" position="top-right">
      <div class="layout-panel">
        <v-btn title="Toggle Dark Mode" @click="toggleDarkMode">
          <v-icon>
            {{ isDarkMode ? 'mdi-white-balance-sunny' : 'mdi-moon-waning-crescent' }}
          </v-icon>
        </v-btn>
      </div>
    </Panel>
    <!-- 小地图 -->
    <MiniMap pannable zoomable />
    <!-- 控制器 -->
    <Controls />
  </VueFlow>

  <!-- 失败对话框 -->
  <v-dialog v-model="ErrDialog" max-width="400">
    <v-card>
      <v-card-title class="headline">错误</v-card-title>
      <v-card-text>{{ errorMessage }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn 
        color="primary"
        @click="ErrDialog = false;
        emit('updateWorkflowDialog', false);
        console.log(workflowUuid)
        ">确定</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

</template>

<style>
/* 导入 Vue Flow 所需的样式 */
@import '@vue-flow/core/dist/style.css';

/* 导入默认主题，这是可选的，但通常推荐 */
@import '@vue-flow/core/dist/theme-default.css';

/* 自定义节点样式 */
/* 暗黑模式 */
/* .v-application {
  background-color: #1e1e1e;
}

.vue-flow__node-default {
  border: 1px solid #fff;
} */

.vue-flow__node-default, .vue-flow__node-input, .vue-flow__node-output {
  font-size: 16px;
}

.loading-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}
</style>