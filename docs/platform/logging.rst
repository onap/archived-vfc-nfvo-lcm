.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Logging & Diagnostic Information
--------------------------------

VF-C logs are kept inside the docker containers: /var/log/onap/vfc/nslcm/runtime_nslcm.log
You can get the log when the dockers start.

Where to Access Information
+++++++++++++++++++++++++++

Use kubectl commands to get the log.
::

    # get the vfc-nslcm pod name
    kubectl -n onap get pod | grep -i vfc
    kubectl -n onap logs dev-vfc-nslcm-6dd99f94f4-vxdkc -c vfc-nslcm

Or:
::

     kubectl -n onap exec -it dev-vfc-nslcm-6dd99f94f4-vxdkc -c vfc-nslcm -- bash
     cd /var/log/onap/vfc/nslcm/
     tail -f runtime_nslcm.log


