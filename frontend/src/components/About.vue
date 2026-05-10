<template>
    <div class="text-center pa-4">
      <v-btn icon @click="dialog = true">
      <v-icon>mdi-information</v-icon>
      </v-btn>

      <v-dialog
        v-model="dialog"
        width="auto"
      >
        <v-card
          width="500px"
          prepend-icon="mdi-information"
          title="关于本网站"
        >
        <v-card-text>
          <v-table>
            <thead>
              <tr>
                <th class="text-left">
                  分工
                </th>
                <th class="text-left">
                  贡献者
                </th>
              </tr>
            </thead>
            <tbody>
            <tr
              v-for="item in about"
              :key="item.work"
            >
              <td>{{ item.work }}</td>
              <td>{{ item.name }}</td>
            </tr>
          </tbody>
          </v-table>
        </v-card-text>
          <template v-slot:actions>
            <v-btn
              class="ms-auto"
              text="Ok"
              @click="dialog = false"
            ></v-btn>
          </template>
        </v-card>
      </v-dialog>
    </div>
  </template>
<script lang="ts">
import { defineComponent } from "vue";

interface AboutItem {
  work: string;
  name: string;
}

export default defineComponent({
  data() {
    return {
      dialog: false as boolean, // 定义类型
      about: [
        {
          work: "网页全栈开发",
          name: "郎程闰",
        },
      ] as AboutItem[], // 使用类型注解
    };
  },
});
</script>