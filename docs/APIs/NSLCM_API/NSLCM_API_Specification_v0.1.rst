

NS LCM API
==========

 {
   "swagger": "2.0",

   "info": {

     "version": "1.0.0",

     "title": "ONAP VFC Network Service Lifecycle Management API",

     "description": "VFC Network Service Lifecycle Management Rest API.",

     "contact": {

       "name": "ONAP VFC team",

       "email": "onap-discuss@lists.onap.org",

       "url": "https://gerrit.onap.org/r/#/admin/projects/vfc/nfvo/lcm"

     }

   },

   "basePath": "/api/nslcm/v1",

   "schemes": [

     "http",
     "https"

   ],

   "consumes": [

     "application/json"

   ],
   "produces": [

     "application/json"

   ],
   "paths": {

     "/ns": {

       "post": {

         "tags": [

           "ns"

         ],
         "summary": "ns create",

         "description": "ns create",

         "operationId": "ns_create",

         "parameters": [

           {

             "in": "body",

             "name": "NSCreateRequest",

             "description": "NS Instance Create Request",

             "required": true,

             "schema": {

               "$ref": "#/definitions/NsCreateRequest"

             }

           }

         ],

         "responses": {

           "200": {

             "description": "successful operation",

             "schema": {

               "$ref": "#/definitions/NsCreateResponse"

             }

           }

         }

       },

       "get": {

         "tags": [

           "ns"

         ],

         "summary": "ns get",

         "description": "ns get",

         "operationId": "ns_get",

         "parameters": [],

         "responses": {

           "200": {

             "description": "successful operation",

             "schema": {

               "$ref": "#/definitions/NsInfo"

             }

           }

         }

       }

     },

     "/ns/{nsInstanceId}/Instantiate": {

       "post": {

         "tags": [

           "ns"

         ],

         "summary": "ns Instantiate",

         "description": "ns Instantiate",

         "operationId": "ns_Instantiate",

         "parameters": [

           {
             "required": true,

             "type": "string",

             "description": "",

             "name": "nsInstanceId",

             "in": "path"

           },
           {

             "in": "body",

             "name": "NSInstantiateRequest",

             "description": "NS Instantiate Request Body",

             "required": true,

             "schema": {

               "$ref": "#/definitions/NsInstantiateRequest"

             }

           }

         ],

         "responses": {

           "200": {

             "description": "",

             "schema": {

               "$ref": "#/definitions/JobInfo"

             }

           },

           "201": {

             "description": "Invalid Request"

           }

         }

       }

     },

     "/ns/{nsInstanceId}/scale": {

       "post": {

         "tags": [

           "ns"

         ],

         "summary": "ns scale",

         "description": "ns scale",

         "operationId": "ns_scale",

         "parameters": [

           {

             "required": true,

             "type": "string",

             "description": "",

             "name": "nsInstanceId",

             "in": "path"

           },

           {

             "in": "body",

             "name": "ScaleNSRequest",

             "description": "Scale NS Request Body",

             "required": true,

             "schema": {

               "$ref": "#/definitions/NsScaleRequest"

             }

           }

         ],

         "responses": {

           "200": {

             "description": "",

             "schema": {

               "$ref": "#/definitions/JobInfo"

             }

           },

           "201": {

             "description": "Invalid Request"

           }

         }

       }

     },

     "/ns/{ns_instance_id}/heal": {

       "post": {

         "tags": [

           "ns"

         ],

         "summary": "ns heal",

         "description": "ns heal",

         "operationId": "ns_heal",

         "parameters": [

           {
             "required": true,

             "type": "string",

             "description": "Identifier of the NS instance.",

             "name": "ns_instance_id",

             "in": "path"

           },

           {

             "in": "body",

             "name": "healVnfData",

             "description": "healVnfData",

             "required": true,

             "schema": {

               "$ref": "#/definitions/NsHealRequest"

             }

           }

         ],

         "responses": {

           "202": {

             "description": "",

             "schema": {

               "$ref": "#/definitions/JobInfo"

             }

           },

           "500": {

             "description": "the url is invalid"

           }

         }

       }

     },

     "/ns/{ns_instance_id}/terminate": {

       "post": {

         "tags": [

           "ns"

         ],

         "summary": "ns terminate",

         "description": "ns terminate",

         "operationId": "ns_terminate",

         "parameters": [

           {

             "required": true,

             "type": "string",

             "description": "Identifier of the NS instance.",

             "name": "ns_instance_id",

             "in": "path"

           },

           {
             "in": "body",

             "name": "NsTerminateRequest",

             "description": "NsTerminateRequest",

             "required": true,

             "schema": {

               "$ref": "#/definitions/NsTerminateRequest"

             }

           }

         ],

         "responses": {

           "202": {

             "description": "",

             "schema": {

               "$ref": "#/definitions/JobInfo"

             }

           },

           "500": {

             "description": "the url is invalid"

           }

         }

       }

     },
     "/ns/{ns_instance_id}": {

       "delete": {

         "tags": [

           "ns"

         ],

         "summary": "ns delete",

         "description": "ns delete",

         "operationId": "ns_delete",

         "parameters": [

           {
             "required": true,

             "type": "string",

             "description": "Identifier of the NS instance.",

             "name": "ns_instance_id",

             "in": "path"

           }

         ],

         "responses": {

           "204": {

             "description": "The NS instance resource and the associated NS identifier were deleted successfully."

           }

         }

       }

     },

     "/jobs/{jobId}": {

       "post": {

         "tags": [

           "job"

         ],

         "summary": "jobstatus",

         "description": "",

         "operationId": "jobstatus",

         "parameters": [

           {
             "required": true,

             "type": "string",

             "description": "",

             "name": "jobId",

             "in": "path"

           },

           {

             "in": "body",

             "name": "body",

             "description": "request param",

             "required": true,

             "schema": {

               "$ref": "#/definitions/JobProgressRequest"

             }

           }

         ],

         "responses": {

           "202": {

             "description": ""

           }

         }

       }

     }

   },

   "definitions": {

     "NsCreateRequest": {

       "type": "object",

       "properties": {

         "context":{

            "type": "object",

            "properties": {

              "globalCustomerId":{

                 "type": "string",
                 "description": "the global customer id"

              },

              "serviceType":{
                 "type": "string",

                 "description": "service type"

              }

            }

         },

         "csarId": {

           "type": "string",

           "description": "the NS package ID"

         },

         "nsName": {

           "type": "string"

         },

         "description": {

           "type": "string"

         }

       }

     },

     "NsCreateResponse": {

       "type": "object",

       "properties": {

         "nsInstanceId": {

           "type": "string"

         }

       }

     },
     "NsInstantiateRequest": {

       "type": "object",

       "properties": {

         "LocationConstraints": {

           "type": "array",

           "items": {

             "$ref": "#/definitions/LocationConstraint"

           }

         },

         "additionalParamForNs": {

           "type": "string"

         }

       }

     },

     "LocationConstraint": {

       "type": "object",

       "properties": {

         "vnfProfileId": {

           "type": "string"

         },
         "locationConstraints": {

           "type": "object",

           "properties": {

             "vimid": {

               "type": "string"

             }

           }

         }

       }

     },

     "NsScaleRequest": {

       "type": "object",

       "properties": {

         "scaleType": {

           "type": "string"

         },

         "scaleNsByStepsData": {

           "$ref": "#/definitions/NsScaleByStepsData"

         }

       }

     },

     "NsScaleByStepsData": {

       "type": "object",

       "properties": {

         "scalingDirection": {

           "type": "string"

         },

         "aspectId": {

           "type": "string"

         },

         "numberOfSteps": {

           "type": "integer"

         }

       }

     },

     "NsHealRequest": {

       "type": "object",

       "properties": {

         "vnfInstanceId": {

           "type": "string"

         },

         "cause": {

           "type": "string"

         },

         "additionalParams": {

           "type": "object",

           "properties": {

             "action": {

               "type": "string"

             },

             "actionvminfo": {

               "type": "object",

               "properties": {

                 "vmid": {

                   "type": "string"

                 },

                 "vmname": {

                   "type": "string"

                 }

               }

             }

           }

         }

       }

     },

     "NsTerminateRequest": {

       "type": "object",

       "properties": {

         "terminationType": {

           "type": "string"

         },

         "gracefulTerminationTimeout": {

           "type": "string"

         }

       }

     },

     "JobInfo": {

       "type": "object",

       "properties": {

         "jobId": {

           "type": "string"

         }

       }

     },

     "JobProgressRequest": {

       "type": "object",

       "properties": {

         "progress": {

           "type": "string"

         },

         "desc": {

           "type": "string"

         },

         "errcode": {

           "type": "string"

         }

       }

     },

     "NsInfo": {

       "type": "object",

       "properties": {

         "nsInstanceId": {

           "type": "string"

         },

         "nsName": {

           "type": "string"

         },

         "description": {

           "type": "string"

         },

         "nsdId": {

           "type": "string"

         },

         "vnfInfo": {

           "type": "array",

           "items": {

             "$ref": "#/definitions/vnfInfo"

           }

         },

         "vlInfo": {

           "type": "array",

           "items": {

             "$ref": "#/definitions/vlInfo"

           }

         },

         "vnffgInfo": {

           "type": "array",

           "items": {

             "$ref": "#/definitions/vnffgInfo"

           }

         },

         "nsState": {

           "type": "string"

         }

       }

     },

     "vnfInfo": {

       "type": "object",

       "properties": {

         "vnfInstanceId": {

           "type": "string"

         },

         "vnfInstanceName": {

           "type": "string"

         },

         "vnfdId": {

           "type": "string"

         }

       }

     },

     "vlInfo": {

       "type": "object",

       "properties": {

         "vlInstanceId": {

           "type": "string"

         },

         "vlInstanceName": {

           "type": "string"

         },

         "vldId": {

           "type": "string"

         },

         "relatedCpInstanceId": {

           "type": "array",

           "items": {

             "$ref": "#/definitions/cpInfo"

           }

         }

       }

     },

     "cpInfo": {

       "type": "object",

       "properties": {

         "cpInstanceId": {

           "type": "string"

         },

         "cpInstanceName": {

           "type": "string"

         },

         "cpdId": {

           "type": "string"

         }

       }

     },
     "vnffgInfo": {

       "type": "object",

       "properties": {

         "vnffgInstanceId": {

           "type": "string"

         },

         "vnfId": {

           "type": "string"

         },
         "pnfId": {

           "type": "string"

         },

         "virtualLinkId": {

           "type": "string"

         },

         "cpId": {

           "type": "string"

         },

         "nfp": {

           "type": "string"

         }

       }

     }

   }

 }