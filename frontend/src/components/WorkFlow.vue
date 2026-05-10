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
</template>

<script setup lang="ts">
import { Position, VueFlow, Panel } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { MiniMap } from '@vue-flow/minimap';
import { Controls } from '@vue-flow/controls';
import dagre from '@dagrejs/dagre';
import { ref, onMounted } from 'vue';
import { countObjects } from '@/utils/vueflow';
// import { generateColors } from '@/utils/vueflow';
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

// 初始化 dagre 图
const g = new dagre.graphlib.Graph();
g.setGraph({
  rankdir: 'LR', // 布局方向（左到右）
  nodesep: 80, // 水平间距
  edgesep: 10, // 边与节点之间的距离
  ranksep: 30, // 行距（节点之间的垂直间距）
});
g.setDefaultEdgeLabel(() => ({}));

// 响应式数据
const inputData = ref<any>(null);
const nodes = ref<any[]>([]);
const edges = ref<any[]>([]);
const isDarkMode = ref(false);

// 切换暗黑模式的方法
const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value; // 切换模式
      applyStyles(isDarkMode); // 调用方法应用样式
    };

// 加载数据并处理图布局
const isWorkflowLoading = ref(false);
const fetchData = async () => {
  try {
    isWorkflowLoading.value = true; // 开始加载
    const response = await fetch('/api/dot2json');
    if (!response.ok) throw new Error('Failed to fetch data');
    inputData.value = await response.json();
    // 把object里面的label属性中的n替换成html可以解析的换行符
    inputData.value.dag.objects.forEach((node: any) => {
      node.label = node.label.replace(/\\n/g, ' for ');
    });
    // 统计对象数量
    const objectNum = countObjects(inputData.value);

    // 生成颜色
    // const colors = generateColors(objectNum);

    console.log(inputData.value);

    // 定义节点和边
    const graphNodes = inputData.value.dag.objects.map((node: any) => ({
      id: node.name,
      label: node.label,
      width: 250,
      height: 50,
      // style: { backgroundColor: colors[node._gvid] },
    }));

    const graphEdges = inputData.value.dag.edges.map((edge: any) => ({
      source: edge.tail.toString(),
      target: edge.head.toString(),
    }));

    // 添加节点到图
    graphNodes.forEach((node: any) => {
      g.setNode(node.id, {
        label: node.label,
        width: node.width,
        height: node.height,
        style: node.style,
      });
    });

    // 添加边到图
    graphEdges.forEach((edge: any) => {
      g.setEdge(edge.source, edge.target);
    });

    // 运行布局
    dagre.layout(g);

    // 获取布局后的节点和边
    nodes.value = g.nodes().map((nodeId) => {
      const node: any = g.node(nodeId);
      const nodeStatus = getNodeStatus(nodeId, inputData.value);
      return {
        id: nodeId,
        type: nodeStatus, // 根据节点状态设置类型
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        position: { x: node.x, y: node.y },
        data: { label: node.label },
        style: node.style,
      };
    });

    edges.value = g.edges().map((edgeObj) => {
      return {
        id: `e${edgeObj.v}->${edgeObj.w}`,
        source: edgeObj.v,
        target: edgeObj.w,
      };
    });
  } catch (error) {
    console.error(error);
  }finally {
    isWorkflowLoading.value = false; // 加载完成
  }
};

// 根据节点 ID 获取节点状态
const getNodeStatus = (nodeId: string, data: any) => {
  const completedNodes = data.completed.split(',').map((id: string) => id.trim());
  const ongoingNodes = data.ongoing.split(',').map((id: string) => id.trim());
  const unfinishedNodes = data.unfinished.split(',').map((id: string) => id.trim());

  if (completedNodes.includes(nodeId)) {
    return 'complete'; // 已完成
  } else if (ongoingNodes.includes(nodeId)) {
    return 'loading'; // 进行中
  } else if (unfinishedNodes.includes(nodeId)) {
    return 'waiting'; // 未完成
  } else {
    return 'default'; // 默认类型
  }
};
// 组件挂载时加载数据
onMounted(fetchData);
</script>

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