--
-- Copyright  2017 ZTE Corporation.
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
--

/******************drop old database and user***************************/
use mysql;
drop database IF  EXISTS vfcnfvolcm;
delete from user where User='vfcnfvolcm';
FLUSH PRIVILEGES;

/******************create new database and user***************************/
create database vfcnfvolcm CHARACTER SET utf8;

GRANT ALL PRIVILEGES ON vfcnfvolcm.* TO 'vfcnfvolcm'@'%' IDENTIFIED BY 'vfcnfvolcm' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON mysql.* TO 'vfcnfvolcm'@'%' IDENTIFIED BY 'vfcnfvolcm' WITH GRANT OPTION;

GRANT ALL PRIVILEGES ON vfcnfvolcm.* TO 'vfcnfvolcm'@'localhost' IDENTIFIED BY 'vfcnfvolcm' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON mysql.* TO 'vfcnfvolcm'@'localhost' IDENTIFIED BY 'vfcnfvolcm' WITH GRANT OPTION;
FLUSH PRIVILEGES; 