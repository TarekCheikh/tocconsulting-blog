/*
 *  oracle_oci_demo.c
 *  example program to show how to perform a simple SELECT request
 *  using Oracle oci library (Oracle Call Interface API)
 */

#include <oci.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Service name as defined inside tnsnames.ora */
#define CONNECTION_STRING "ORCLUBUNTU"

#define OK 0
#define KO 1

#define BUFFER_SIZE 512

/*
 * The description of the table "empployees" used in this example is
 * shown below :
SQL> desc employees;
Name					   Null?    	Type
----------------------------------------- -------- ----------------------------
EMPLOYEE_ID				   NOT NULL 	NUMBER(6)
FIRST_NAME					    		VARCHAR2(20)
LAST_NAME				   NOT NULL 	VARCHAR2(25)
EMAIL					   NOT NULL 	VARCHAR2(25)
PHONE_NUMBER					    	VARCHAR2(20)
HIRE_DATE				   NOT NULL 	DATE
JOB_ID 				   	   NOT NULL 	VARCHAR2(10)
SALARY 					    			NUMBER(8,2)
COMMISSION_PCT 				    		NUMBER(2,2)
MANAGER_ID					    		NUMBER(6)
DEPARTMENT_ID					    	NUMBER(4)
 */

/* Number of columns returned by our request */
#define NUM_FETCHED_COLUMNS 4
/* FIRST_NAME column length */
#define FIRST_NAME_LEN 20
#define LAST_NAME_LEN 25
#define SELECT_STRING	"SELECT department_id, first_name, last_name, salary " \
			"FROM HR.employees WHERE department_id is not null"

/* Oracle connection parameters */
text *username = (text *)"hr";
text *password = (text *)"human";

int main(int argc, char **argv) {
	/* OCI environment handle */
	OCIEnv *env_handle = NULL;
	/* The server handle */
	OCIServer *server_handle = NULL;
	/* The error handle */
	OCIError *error_handle = NULL;
	/* OCI user session handle */
	OCISession *user_session_handle = NULL;
	/* OCI service context handle */
	OCISvcCtx *service_handle = NULL;
	sword errcode = 0;
	text errbuf[BUFFER_SIZE];
	/* OCI statement handle */
	OCIStmt *statement_handle = (OCIStmt *)0;
	/* OCI define handle */
	OCIDefine *defhp[NUM_FETCHED_COLUMNS];
	text select_query[256];
	ub4 emp_department_id = 0;
	text emp_first_name[FIRST_NAME_LEN + 1];
	text emp_last_name[LAST_NAME_LEN + 1];
	float emp_salary = 0.0;

	/* Step 1 : Creating our environment */
	errcode =
		OCIEnvCreate(&env_handle, OCI_DEFAULT, NULL, NULL, NULL,
				NULL, 0, NULL);
	if (errcode != 0) {
		fprintf(stderr, "OCIEnvCreate failed with errcode = %d.\n",
			errcode);
		return KO;
	}

	/*
	 * Step 2 : Memory allocation for all handles:
	 * error_handle, service_handle, server_handle and user_session_handle
	 */

	errcode = OCIHandleAlloc((void *)env_handle, (void **)&error_handle,
			OCI_HTYPE_ERROR, 0, NULL);
	if (errcode == OCI_INVALID_HANDLE) {
		fprintf(stderr, "OCIHandleAlloc failed for 'error_handle' with"
				" errcode = %d.\n",
				errcode);
		return KO;
	}
	errcode = OCIHandleAlloc((void *)env_handle, (void **)&service_handle,
			OCI_HTYPE_SVCCTX, 0, NULL);
	if (errcode == OCI_INVALID_HANDLE) {
		fprintf(stderr,
			"OCIHandleAlloc failed for 'service_handle' with "
			"errcode = %d.\n", errcode);
		return KO;
	}
	errcode = OCIHandleAlloc((void *)env_handle, (void **)&server_handle,
			OCI_HTYPE_SERVER, 0, NULL);
	if (errcode == OCI_INVALID_HANDLE) {
		fprintf(stderr,
			"OCIHandleAlloc failed for 'server_handle' with "
			"errcode = %d.\n", errcode);
		return KO;
	}
	errcode = OCIHandleAlloc((void *)env_handle,
			(void **)&user_session_handle, OCI_HTYPE_SESSION,
			0, NULL);
	if (errcode == OCI_INVALID_HANDLE) {
		fprintf(stderr,
			"OCIHandleAlloc failed for 'user_session_handle' "
			"with errcode = %d.\n", errcode);
		return KO;
	}
	/* End of memory allocations */

	/* Step 3: Create a server context */
	OCIServerAttach(server_handle, error_handle, (text *)CONNECTION_STRING,
			strlen(CONNECTION_STRING), OCI_DEFAULT);
	/* Step 4: Set the server attribute in the service context handle */
	OCIAttrSet((void *)service_handle, OCI_HTYPE_SVCCTX,
			(void *)server_handle, (ub4)0, OCI_ATTR_SERVER,
			error_handle);
	/* Step 5:  Set user name attribute in user session handle */
	OCIAttrSet((void *)user_session_handle, OCI_HTYPE_SESSION,
			(void *)username, (ub4)strlen((char *)username),
			OCI_ATTR_USERNAME, error_handle);
	/* Step 6: Set password attribute in user session handle  */
	OCIAttrSet((void *)user_session_handle, OCI_HTYPE_SESSION,
			(void *)password, (ub4)strlen((char *)password),
			OCI_ATTR_PASSWORD, error_handle);
	/* Step 7: Set the user session attribute in the service context
	   handle */
	OCIAttrSet((void *)service_handle, OCI_HTYPE_SVCCTX,
			(void *)user_session_handle, (ub4)0, OCI_ATTR_SESSION,
			error_handle);
	/* Step 8:  Establish a session to the Oracle server */
	errcode = OCISessionBegin(service_handle, error_handle, user_session_handle,
			OCI_CRED_RDBMS, (ub4)OCI_DEFAULT);
	if (errcode == OCI_ERROR) {
		OCIErrorGet((dvoid *)error_handle, (ub4)1, (text *)NULL,
				&errcode, errbuf, (ub4)sizeof(errbuf),
				OCI_HTYPE_ERROR);
		fprintf(stdout, "Error - %.*s\n", 512, errbuf);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}
	/* At this stage we are connected to the server */
	fprintf(stdout, "Connection succeed\n");
	/* Fin de l'etape 2 */

	strcpy(select_query, SELECT_STRING);
	/* Allovating memory for our request */
	errcode = OCIHandleAlloc(env_handle, (dvoid **)&statement_handle,
			OCI_HTYPE_STMT, (size_t)0, (dvoid **)0);
	if (errcode == OCI_INVALID_HANDLE) {
		fprintf(stderr, "OCIHandleAlloc : statement_handle failed "
				"with errcode = %d.\n",
				errcode);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}
	/*  Prepare the request */
	errcode = OCIStmtPrepare(statement_handle, error_handle,
				(text *)select_query,
				(ub4)strlen((const signed char *)select_query),
				OCI_NTV_SYNTAX, OCI_DEFAULT);
	if (errcode != OCI_SUCCESS) {
		fprintf(stderr, "OCIStmtPrepare failed with errcode = "
				"%d.\n",
				errcode);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}

	/* Corresponding variables with their positions inside the request :
	 * emp_department_id ==> department_id (position 1 and of type int)
	 * emp_first_name    ==> first_name (position 2 and of type string)
	 * emp_last_name     ==> last_name (position 3 and of type string)
	 * emp_salary        ==> salary (position 4 and of type float)
	 */
	errcode = OCIDefineByPos(statement_handle, &defhp[0], error_handle,
				(ub4)1, (dvoid *)&emp_department_id,
				(sb4)sizeof(ub4), (ub2)SQLT_INT, (dvoid *)0,
				(ub2 *)0, (ub2 *)0, OCI_DEFAULT);
	if (errcode != OCI_SUCCESS) {
		fprintf(stderr, "OCIDefineByPos : emp_department_id failed "
				"with errcode = %d.\n",
				errcode);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}
	errcode = OCIDefineByPos(statement_handle, &defhp[1], error_handle,
				(ub4)2, (dvoid *)&emp_first_name,
				(sb4)sizeof(emp_first_name), (ub2)SQLT_STR,
				(dvoid *)0, (ub2 *)0, (ub2 *)0, OCI_DEFAULT);
	if (errcode != OCI_SUCCESS) {
		fprintf(stderr, "OCIDefineByPos : emp_first_name failed "
				"with errcode = %d.\n",
				errcode);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}
	errcode = OCIDefineByPos(statement_handle, &defhp[2], error_handle,
				(ub4)3, (dvoid *)&emp_last_name,
				(sb4)sizeof(emp_last_name), (ub2)SQLT_STR,
				(dvoid *)0, (ub2 *)0, (ub2 *)0, OCI_DEFAULT);
	if (errcode != OCI_SUCCESS) {
		fprintf(stderr, "OCIDefineByPos : emp_last_name failed "
				"with errcode = %d.\n",
				errcode);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}
	errcode =
		OCIDefineByPos(statement_handle, &defhp[3], error_handle,
				(ub4)4, (dvoid *)&emp_salary,
				(sb4)sizeof(float), (ub2)SQLT_FLT, (dvoid *)0,
				(ub2 *)0, (ub2 *)0, OCI_DEFAULT);
	if (errcode != OCI_SUCCESS) {
		fprintf(stderr, "OCIDefineByPos : emp_salary failed "
				"with errcode = %d.\n",
				errcode);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}

	/* Execute the request */
	errcode =
		OCIStmtExecute(service_handle, statement_handle,
				error_handle, (ub4)0, (ub4)0, (OCISnapshot *)0,
				(OCISnapshot *)0, OCI_DEFAULT);
	if (errcode != OCI_SUCCESS) {
		OCIErrorGet((dvoid *)error_handle, (ub4)1, (text *)NULL,
				&errcode, errbuf, (ub4)sizeof(errbuf),
				OCI_HTYPE_ERROR);
		fprintf(stdout, "Error - %.*s\n", 512, errbuf);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}

	/* Get the result of the request */
	errcode = OCIStmtFetch2(statement_handle, error_handle, 1,
			OCI_FETCH_NEXT, (sb4)0, OCI_DEFAULT);
	if (errcode == OCI_NO_DATA) {
		fprintf(stdout, "No data found for this request!\n");
	} else if (errcode != OCI_SUCCESS) {
		OCIErrorGet((dvoid *)error_handle, (ub4)1, (text *)NULL,
				&errcode, errbuf, (ub4)sizeof(errbuf),
				OCI_HTYPE_ERROR);
		fprintf(stdout, "Error - %.*s\n", 512, errbuf);
		OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
		return KO;
	}

	while (errcode == OCI_SUCCESS) {
		fprintf(stdout, "Emp_First_Name : %s -- Emp_Last_name : %s -- "
				"Emp_Deptno : %u -- Sal : %.2f\n",
				emp_first_name, emp_last_name,
				emp_department_id, emp_salary);
		errcode = OCIStmtFetch2(statement_handle,
					error_handle, 1, OCI_FETCH_NEXT,
					(sb4)0, OCI_DEFAULT);
	}

	/* Close session, Detach server, release memory and terminate
	   OCI process */
	OCISessionEnd(service_handle, error_handle, user_session_handle,
			OCI_DEFAULT);
	OCIServerDetach(server_handle, error_handle, OCI_DEFAULT);
	OCIHandleFree((dvoid *)env_handle, OCI_HTYPE_ENV);
	OCITerminate(OCI_DEFAULT);

	return 0;
}
