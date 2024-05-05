import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    row: {},
    isFromDetail: false,
  },
  mutations: {
    setRow(state, payload){
      state.row = payload
    },
    clearRow(state){
      state.row = {}
    },
    changeIsFromDetail(state, payload){
      state.isFromDetail = payload
    },
  },
  actions: {
  },
  modules: {
  }
})
