<template>
  <v-card class="mx-auto ma-10 pa-4" elevation="2" max-width="950">
    <v-card-title>Top Clerks</v-card-title>
      <v-container>
        <v-row class="text-center">
          <v-col cols="12">
            <v-card-subtitle>
              Choose Date Range
            </v-card-subtitle>
          </v-col>
        </v-row>

        <v-row justify="space-around">
          <v-col cols="6">
            <v-menu
              v-model="menu_begin"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-text-field
                  v-model="begin"
                  label="Beginning of window"
                  prepend-icon="mdi-calendar"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="begin"
                @input="menu_begin = false"
                min="1992-01-01"
                max="1992-01-10"
                color="green lighten-1"
              ></v-date-picker>
            </v-menu>
          </v-col>
          <v-col cols="6">
            <v-menu
              v-model="menu_end"
              :close-on-content-click="false"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-text-field
                  v-model="end"
                  label="End of window"
                  prepend-icon="mdi-calendar"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="end"
                @input="menu_end = false"
                min="1992-01-01"
                max="1992-01-10"
                color="primary"
                header-color="primary"
              ></v-date-picker>
            </v-menu>
          </v-col>
        </v-row>
        <v-row justify="space-around" class="mt-6">
          <v-slider
            v-model="topn"
            hint="TopN"
            min="1" max="30"
            persistent-hint
            thumb-label="always"
          >
          </v-slider>
        </v-row>
        <v-divider class="my-10"></v-divider>
        <v-row justify="space-around" class="ma-10">
          <v-simple-table dense>
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">
                    O_CLERK
                  </th>
                  <th class="text-left">
                    CLERK_TOTAL
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in clerk_data"
                  :key="item.O_CLERK"
                >
                  <td>{{ item.O_CLERK }}</td>
                  <td>{{ item.CLERK_TOTAL }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-row>
    </v-container>
  </v-card>
</template>

<script>
import axios from 'axios'
export default {
  name: 'TopClerks',

  data: () => ({
    begin: "1992-01-02",
    end: "1992-01-09",
    topn: 10,
    menu_begin: false,
    menu_end: false,
    clerk_data: {},
  }),
  mounted() {
    this.get_data()
  },
  watch: {
    begin() {
      this.get_data()
    },
    end() {
      this.get_data()
    },
    topn() {
      this.get_data()
    },
  },
  methods: {
    get_data() {
      const baseUrl = process.env.VUE_APP_API_URL
      axios.get(baseUrl + "/top_clerks", 
                {params: {start_range: this.begin, end_range: this.end, topn: this.topn}})
        .then(r => {
          this.clerk_data = r.data
        })
        .catch(function (error) {
          console.log("Error reading top_clerks:" + error)
        })
    }
  }

}
</script>
