<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
    >
    <v-row>
      <v-col cols="1">
        <v-img src="https://upload.wikimedia.org/wikipedia/commons/f/ff/Snowflake_Logo.svg" 
          contain :aspect-ratio="184/44" height="40"
        ></v-img>
      </v-col>
      <v-col cols="10"  class="text-center">
        <v-toolbar-title>Simple Clerks App</v-toolbar-title>    
      </v-col>
      <v-col cols="1"></v-col>
    </v-row>

  </v-app-bar>

    <v-main>
      <TopClerks/>
    </v-main>
  </v-app>
</template>

<script>
import TopClerks from './components/TopClerks';

export default {
  name: 'App',

  components: {
    TopClerks,
  },

  data: () => ({
    //
  }),
};
</script>
