<template>
  <div>
    <!-- First Row: Input card and prediction button -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="box-card" shadow="never">
          <div slot="header" class="clearfix">
            <span class="card-header">Make a Prediction</span>
          </div>
          <div style="margin-bottom: 20px;">
            <el-select v-model="selectedTicker" filterable placeholder="Enter a ticker">
              <el-option label="Tesla (TSLA)" value="TSLA"></el-option>
              <el-option label="NVIDIA (NVDA)" value="NVDA"></el-option>
              <el-option label="Apple (AAPL)" value="AAPL"></el-option>
            </el-select>
          </div>
          <el-button type="primary" @click="predict">Predict</el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- Second Row: Prediction details (all tables within the same card) -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card" shadow="never">
          <div slot="header" class="clearfix">
            <span class="card-header">Prediction Details</span>
          </div>

          <!-- Prediction Result Table -->
          <el-table :data="predictionResult" style="width: 100%; margin-bottom: 20px;" border>
            <el-table-column prop="attribute" label="Prediction Result" width="280"></el-table-column>
            <el-table-column prop="value" label="Value"></el-table-column>
          </el-table>

          <!-- Company Info Table -->
          <el-table :data="companyInfo" style="width: 100%; margin-bottom: 20px;" border>
            <el-table-column prop="attribute" label="Company Information" width="280"></el-table-column>
            <el-table-column prop="value" label="Value"></el-table-column>
          </el-table>

          <!-- Variables Used Table -->
          <el-table :data="predictionVariables" style="width: 100%" border>
            <el-table-column prop="attribute" label="Variables Used" width="280"></el-table-column>
            <el-table-column prop="value" label="Value"></el-table-column>
          </el-table>

        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      selectedTicker: null,
      predictionResult: [],
      companyInfo: [],
      predictionVariables: [],
    };
  },
  methods: {
    predict() {
        axios.get(`http://127.0.0.1:8080/backendApp/getDataForStock/${this.selectedTicker}`).then(response => {
          this.predictionResult = response.data.predictionResult;
          this.companyInfo = response.data.companyInfo;
          this.predictionVariables = response.data.predictionVariables;
        }).catch(error => {
            console.error("Error:", error);
        });
    }
  },
}
</script>

<style scoped>
.clearfix:before,
.clearfix:after {
  display: table;
  content: " ";
  clear: both;
}

.card-header {
  font-weight: bold;
  font-size: 20px;
}

.box-card {
  margin-bottom: 20px;
}
</style>