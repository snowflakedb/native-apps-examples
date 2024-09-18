CREATE or replace NOTIFICATION INTEGRATION my_email_int
  TYPE=EMAIL
  ENABLED=TRUE
  ALLOWED_RECIPIENTS=(<YOUR_SNOWFLAKE_USER_EMAIL>);
 create database if not exists app_upgrade_state_notification_db;
create schema if not exists sch;
create table if not exists app_upgrade_state_notification_db.sch.upgrade_state_notification(
  CONSUMER_SNOWFLAKE_REGION varchar,  PROVIDER_ACCOUNT_LOCATOR varchar,PACKAGE_NAME varchar, 
  VERSION varchar, PATCH int, UPGRADE_STATE varchar, NOTIFICATION_STATE varchar, UPDATE_AT timestamp);

-- send notification email to app provider

create or replace procedure app_upgrade_state_notification_db.sch.send_app_upgrade_notification(EMAIL varchar)
  returns string
  language javascript
  comment = "set notification email to the app provider about the app upgrade progress"
  execute as caller
AS
$$
  var query = ` select * from app_upgrade_state_notification_db.sch.upgrade_state_notification
         where  NOTIFICATION_STATE = 'NOT_SEND';
    `;
 
  var res  = snowflake.createStatement({sqlText: query}).execute(); 
  var message_completed = "";
  var message_start = "";
  while(res.next()){
    var target = "In region " + res.getColumnValue("CONSUMER_SNOWFLAKE_REGION") 
                + " the app(s) installed from  upgrade for version " + res.getColumnValue("VERSION")  
                + " patch " + res.getColumnValue("PATCH") 
                + " is  " 
    if(res.getColumnValue("UPGRADE_STATE") == "UPGRATE_START"){
      message_start += target + "starting;\n";
    } else {
       message_completed += target + "completed;\n";   
    }
  }
var message = message_start + message_completed;
if(message){

 send_email_query = " call SYSTEM$SEND_EMAIL ('my_email_int', ' "+ EMAIL + "', 'Email Alert: APPs Upgrade Progress.', '"  + message_start + message_completed + "')";

 var send_email_res = snowflake.createStatement({sqlText: send_email_query}).execute();
 if(send_email_res.next()){
  if(send_email_res.getColumnValue(1) ===true){
      var update_query = `update app_upgrade_state_notification_db.sch.upgrade_state_notification 
               set NOTIFICATION_STATE = 'SENT'
               where NOTIFICATION_STATE = 'NOT_SEND'; 
            `;
      snowflake.createStatement({sqlText: update_query}).execute();
  }
 }
}
return "DONE";
$$;

-- A notification email will send when 
--      * the application starts to upgrade for a given snowflake region
--      * the application upgrade completes for a given snowflake region
--      * an application upgrade fails
     
create or replace procedure app_upgrade_state_notification_db.sch.update_app_state_upgrade_notification(EMAIL varchar)
  returns string
  language javascript
  comment = "update the upgrade_state_notification table when the app upgrade states changed based on the APPLICATION_STATE view"
  execute as caller
AS
$$
PROVIDER_ACCOUNT_LOCATOR = "PROVIDER_ACCOUNT_LOCATOR";
const CONSUMER_SNOWFLAKE_REGION = "CONSUMER_SNOWFLAKE_REGION";
const PACKAGE_NAME = "PACKAGE_NAME";
const TARGET_UPGRADE_VERSION = "TARGET_UPGRADE_VERSION";
const TARGET_UPGRADE_PATCH  = "TARGET_UPGRADE_PATCH";
const CURRENT_VERSION = "CURRENT_VERSION";
const CURRENT_PATCH =  "CURRENT_PATCH";
const UPGRADE_STARTED_ON = "UPGRADE_STARTED_ON";
const UPGRADE_STATE = "UPGRADE_STATE";
const STATE_COMPLETED = "UPGRADE_COMPLETED";
const STATE_START = "UPGRADE_START";
const NOT_SEND = "NOT_SEND"
const SENT = "SENT"

const keys_state = [CONSUMER_SNOWFLAKE_REGION, PROVIDER_ACCOUNT_LOCATOR, PACKAGE_NAME];
const columns = keys_state.concat([CURRENT_VERSION, CURRENT_PATCH, TARGET_UPGRADE_VERSION, TARGET_UPGRADE_PATCH, UPGRADE_STARTED_ON, UPGRADE_STATE]);

function getKey(row, keys){
    var keyString = "";
    for(var col of keys){
        keyString += (row[col] + ":");
    }
    return keyString;
}

function update_notification_table( to_update_row, version_patch, to_update_state ){
  var query = `select * from app_upgrade_state_notification_db.sch.upgrade_state_notification
         where CONSUMER_SNOWFLAKE_REGION = ? and PROVIDER_ACCOUNT_LOCATOR = ? and PACKAGE_NAME = ?
             and VERSION = ? and PATCH = ? ;
    `;
  var query_paras = [to_update_row[CONSUMER_SNOWFLAKE_REGION],to_update_row[PROVIDER_ACCOUNT_LOCATOR], 
  to_update_row[PACKAGE_NAME]].concat(version_patch).concat([NOT_SEND]);
  var state_notification_rest  = snowflake.createStatement({sqlText: query, binds: query_paras}).execute(); 
  if(state_notification_rest.next()){
    //not consider rollback case
    if(state_notification_rest.getColumnValue(UPGRADE_STATE) == STATE_START && 
       to_updata_state == STATE_COMPLETED){

      var update_query = `
         update app_upgrade_state_notification_db.sch.upgrade_state_notification 
         set UPGRADE_STATE = ? and UPGRADE_AT = CURRENT_TIMESTAMP() and NOTIFICATION_STATE = "NOT_SEND"
          where CONSUMER_SNOWFLAKE_REGION = ? and PROVIDER_ACCOUNT_LOCATOR = ? and PACKAGE_NAME = ?
             and VERSION = ? and PATCH = ? ;
      `;
      snowflake.createStatement({sqlText: update_query, binds: query_paras}).execute(); 
    }
  }
  else { 
      var insert_query = ` 
       INSERT INTO app_upgrade_state_notification_db.sch.upgrade_state_notification values(?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP());
      `;
      query_paras = query_paras.concat([NOT_SEND]);
      snowflake.createStatement({sqlText: insert_query, binds: query_paras}).execute(); 
  }
}
const q = `
     select * from SNOWFLAKE.DATA_SHARING_USAGE.APPLICATION_STATE 
     where TARGET_UPGRADE_PATCH is not null
     and UPGRADE_STATE != 'FAILED';
`;
const stmt = snowflake.createStatement({sqlText: q});
const res = stmt.execute();
var state_result = {};
while(res.next()){
  var row = {};
  for (var column of columns) {
    row[column] = res.getColumnValue(column);
  }
  var key = getKey(row, keys_state);
  state_result[key] = state_result[key] === undefined ? [row] : state_result[key].concate([row]);
 }

 //sort the query result
 for(const prop  in state_result){
  var num_apps_for_pkg = state_result[prop].length;
  var row_maybe_completed = {};
  var row_maybe_start = {};
  var target_for = [];
  var completed_for = {};
  
  // group the app state by region, app pkg account and app pkg name, current version/patch
  for( var state_for_version of state_result[prop]){
     var key = getKey(state_for_version, ["CURRENT_VERSION", "CURRENT_PATCH"]);
     completed_for[key] = completed_for[key] === undefined ? 1 : (completed_for[key] +1);
     if(state_for_version["TARGET_UPGRADE_VERSION"]){
        if(state_for_version["UPGRADE_STATE"] == "FAILED"){
          // deal with failed
        }
        else { // suppose only one target version/patch. Actually it is possible with two or more target version/patches
           target_for = [state_for_version["TARGET_UPGRADE_VERSION"], state_for_version["TARGET_UPGRADE_PATCH"]];
           row_maybe_completed = state_for_version;
        }
     }
     if(Object.keys(row_maybe_completed).length ==0) {
      row_maybe_completed = state_for_version;
     }
  }

  if(Object.keys(target_for).length >0){
    update_notification_table( row_maybe_completed, 
        [row_maybe_completed["TARGET_UPGRADE_VERSION"], row_maybe_completed["TARGET_UPGRADE_PATCH"]], STATE_START);      
  }
  //should we consider the FAILED and DISABLED?
  if(Object.keys(completed_for).length == 1){

    var version_patch = Object.keys(completed_for)[0];
    // if all apps's current version/patch are the same, 
    // it means the upgrade for the version/patch is completed
    if(completed_for[version_patch] && completed_for[version_patch] == num_apps_for_pkg){          
      update_notification_table( row_maybe_completed, 
        [row_maybe_completed["CURRENT_VERSION"], row_maybe_completed["CURRENT_PATCH"]],  STATE_COMPLETED);
    }
  }else if(Object.keys(completed_for).length == 2){ // there is a case that the two types of version/patch(eg. v1.0 and v1.1) are in COMPLETE state. In this case, we 
          // suppose the one version (v1.0) should be upgrade COMPLETED for all apps  and the other one(v1.1) just start for upgrade
          var version_patch1 = Object.keys(completed_for)[0];
          var version_patch2 = Object.keys(completed_for)[0];
           update_notification_table( row_maybe_completed, 
        [row_maybe_completed["CURRENT_VERSION"], row_maybe_completed["CURRENT_PATCH"]], STATE_START);
        update_notification_table( row_maybe_completed, 
        [row_maybe_completed["CURRENT_VERSION"], row_maybe_completed["CURRENT_PATCH"]],  STATE_START);
  }
 }
var call_send_email_query = "call app_upgrade_state_notification_db.sch.send_app_upgrade_notification('" + EMAIL + "')";
//return call_send_email_query;
 snowflake.createStatement({sqlText: call_send_email_query}).execute(); 
 
return "DONE";
$$
;

call app_upgrade_state_notification_db.sch.update_app_state_upgrade_notification('yong.xu@snowflake.com');

CREATE OR REPLACE TASK app_upgrade_state_notification_db.sch.application_upgrade_notification_task
  SCHEDULE = '720 minutes'  --12 hours
AS call  app_upgrade_state_notification_db.sch.update_app_state_upgrade_notification();

execute task app_upgrade_state_notification_db.sch.application_upgrade_notification_task;

