export default [
    {
      path: "/",
      name: "Layout",
      component:()=>import("../views/LayoutPage.vue"),
      redirect: "/index",
      children: [
        {
          path: "/index",
          name: "index",
          component: ()=>import("../views/index/HomeIndex.vue")
        },
        {
          path: "/sentiment/community",
          name: "community",
          component: ()=>import("../views/sentiment/community/CommunitySentiment.vue")
        },
        {
          path: "/sentiment/media",
          name: "media",
          component: ()=>import("../views/sentiment/media/MediaSentiment.vue")
        },
        {
          path: "/prediction",
          name: "prediction",
          component: ()=>import("../views/prediction/PredictionPage.vue")
        },
      ]
    },
    {
      path: "/login",
      name: "Login",
      component: ()=>import("../views/LoginPage.vue")
    },
    {
      path: "*",
      name: "NotFound",
      component: ()=>import("../views/NotFound.vue")
    }
  ]