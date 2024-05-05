import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import './common/reset.css'
import './common/rule.css'
import './mock/mock'
import "./router/guard"
Vue.config.productionTip = false
import locale from 'element-ui/lib/locale/lang/en'; // Import the English locale
import 'element-ui/lib/theme-chalk/index.css';

Vue.use(ElementUI, { locale });

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
