'use strict';
angular.module('odoo', ['ngCookies']);

'use strict';
angular.module('odoo').provider('jsonRpc', function jsonRpcProvider() {

	this.odooRpc = {
		odoo_server: "",
		uniq_id_counter: 0,
		context: {'lang': 'fr_FR'},
		shouldManageSessionId: false, //try without first
		errorInterceptors: []
	};

	var preflightPromise = null;

	this.$get = ["$http", "$cookies", "$q", "$timeout", function($http, $cookies, $q, $timeout) {

		var odooRpc = this.odooRpc;

		/**
		* get_database_list
		*		Return availables database list
		*/
		odooRpc.get_database_list = function() {
			return odooRpc.sendRequest('/web/database/get_list', {}).then(function(result) {
				return result;
			});
		};

		/**
		* login
		*		update cookie (session_id) in both cases
		* @return promise
		*		resolve promise if credentials ok
		*		reject promise if credentials ko (with {title: wrong_login})
		*		reject promise in other cases (http issues, server error)   
		*/
		odooRpc.login = function(db, login, password) {
			var params = {
				db : db,
				login : login,
				password : password
			};

			return odooRpc.sendRequest('/web/session/authenticate', params).then(function(result) {
				if (!result.uid) {
					delete $cookies.session_id;
					return $q.reject({ 
						title: 'wrong_login',
						message:'Credentials incorrect',
						fullTrace: result
					});
				}
				odooRpc.context = result.user_context;
				$cookies.session_id = result.session_id;
				return result;
			});
		};

		/**
		* check if logged in or not
		* @param force 
		* 		if false -> check the cookies and return boolean
		*		if true -> check with the server if still connected return promise
		* @return boolean || promise
		*
		*/
		odooRpc.isLoggedIn = function (force) {
			if (!force)
				return $cookies.session_id && $cookies.session_id.length > 10;

			return odooRpc.getSessionInfo().then(function (result) {
				return !!(result.uid); 
			});
		};

		/**
		* logout (delete cookie)
		* @param force
		*		if true try to connect with falsy ids
		* @return null || promise 
		*/
		odooRpc.logout = function (force) {
			delete $cookies.session_id;
			if (force)
				odooRpc.getSessionInfo().then(function (r) { //get db from sessionInfo
          if (r.db)
					  odooRpc.login(r.db, '', '');
				});
		};

		odooRpc.searchRead = function(model, domain, fields) {
			var params = {
				model: model,
				domain: domain,
				fields: fields,
			}
			return odooRpc.sendRequest('/web/dataset/search_read', params);
		};

		odooRpc.getSessionInfo = function(model, method, args, kwargs) {
			return odooRpc.sendRequest('/web/session/get_session_info', {});
		};

		odooRpc.getServerInfo = function(model, method, args, kwargs) {
			return odooRpc.sendRequest('/web/webclient/version_info', {});
		};

		odooRpc.syncDataImport = function(model, func_key, domain, limit, object) {
			return odooRpc.call(model, 'get_sync_data', [
				func_key, object.timekey, domain, limit
			], {}).then(function(result) {
					if (object.timekey === result.timekey)
						return; //no change since last run
					object.timekey = result.timekey; 
					
					angular.extend(object.data, result.data);
					
					angular.forEach(object.remove_ids, function(id) {
							delete object.data[id];
					});

					if (result.data.length)
						odooRpc.syncDataImport(model, func_key, domain, limit, object);
			});
		};

		odooRpc.syncImportObject = function(params) {
			/* params = {
					model: 'odoo.model',
					func_key: 'my_function_key',
					domain: [],
					limit: 50,
					interval: 5000,
					}

			 return a synchronized object where you can access
			 to the data using object.data
			*/
			var stop = false;
			var watchers = [];
			var object = { 
				data: {}, 
				timekey: null, 
				stopCallback: function () {
					stop = true;
				},
				watch: function(fun) {
					watchers.push(fun);
				}
			};

			function sync() {

				odooRpc.syncDataImport(
					params.model,
					params.func_key,
					params.domain,
					params.limit,
					object).then(function () { 
						if (!stop)
							$timeout(sync, params.interval);
				}).then(function(data) {
					watchers.forEach(function (fun) {
						fun(object);
					});
				});
			}
			sync();

			return object;
		};

		odooRpc.call = function(model, method, args, kwargs) {

			kwargs = kwargs || {};
			kwargs.context = kwargs.context || {};
			angular.extend(kwargs.context, odooRpc.context);

			var params = {
				model: model,
				method: method,
				args: args,
				kwargs: kwargs,
			};

			return odooRpc.sendRequest('/web/dataset/call_kw', params);
		};


		/**
		* base function
		*/
		odooRpc.sendRequest = function(url, params) {

			/** (internal) build request for $http
			* keep track of uniq_id_counter
			* add session_id in the request (for Odoo v7 only) 
			*/
			function buildRequest(url, params) {
				odooRpc.uniq_id_counter += 1;
				if (odooRpc.shouldManageSessionId)
					params.session_id = $cookies.session_id

				var json_data = {
					jsonrpc: '2.0',
					method: 'call',
					params: params, //payload
				};
				return {
					'method' : 'POST',
					'url' : odooRpc.odoo_server + url,
					'data' : JSON.stringify(json_data),
					'headers': {
						'Content-Type' : 'application/json'
					},
					'id': ("r" + odooRpc.uniq_id_counter),
				};
			}

			/** (internal) Odoo do some error handling and doesn't care
			* about HTTP response code
			* catch errors codes here and reject
			*	@param response $http promise
			*	@return promise 
			*		if no error : response.data ($http.config & header stripped)
			*		if error : reject with a custom errorObj
			*/
			function handleOdooErrors(response) {
				if (!response.data.error)
					return response.data;

				var error = response.data.error;
				var errorObj = {
					title: '',
					message:'',
					fullTrace: error
				};

				if (error.code === 200 && error.message === "Odoo Server Error" && error.data.name === "werkzeug.exceptions.NotFound") {
					errorObj.title = 'page_not_found';
					errorObj.message = 'HTTP Error';
				} else if ( (error.code === 100 && error.message === "Odoo Session Expired") || //v8
							(error.code === 300 && error.message === "OpenERP WebClient Error" && error.data.debug.match("SessionExpiredException")) //v7
						) {
							errorObj.title ='session_expired';
							delete $cookies.session_id;
				} else {
					var split = ("" + error.data.fault_code).split('\n')[0].split(' -- ');
					if (split.length > 1) {
						error.type = split.shift();
						error.data.fault_code = error.data.fault_code.substr(error.type.length + 4);
					}

					if (error.code === 200 && error.type) {
						errorObj.title = error.type;
						errorObj.message = error.data.fault_code.replace(/\n/g, "<br />");
					} else {
						errorObj.title = error.message;
						errorObj.message = error.data.debug.replace(/\n/g, "<br />");
					}
				}
				odooRpc.errorInterceptors.forEach(function (i) {
					i(errorObj);
				});
				return $q.reject(errorObj)
			}

			/**
			*	(internal)
			*	catch HTTP response code (not handled by Odoo ie Error 500, 404)
			*	@params $http rejected promise
 			*	@return promise
			*/
			function handleHttpErrors(reason) {
				var errorObj = {title:'http', fullTrace: reason, message:'HTTP Error'};
				odooRpc.errorInterceptors.forEach(function (i) {
					i(errorObj);
				});
				return $q.reject(errorObj);
			}

			/**
			*	(internal) wrapper around $http for handling errors and build request
			*/
			function http(url, params) {
				var req = buildRequest(url, params);
				return $http(req).then(handleOdooErrors, handleHttpErrors);
			}

			/** (internal) determine if session_id shoud be managed by this lib
			* more info: 
			*	in v7 session_id is returned by the server in the payload 
			*		and it should be added in each request's paylaod.
			*		it's 
			*
			*	in v8 session_id is set as a cookie by the server
			*		therefor the browser send it on each request automatically
			*
			*	in both case, we keep session_id as a cookie to be compliant with other odoo web clients 
			*
			*/
			function preflight() {
				//preflightPromise is a kind of cache and is set only if the request succeed
				return preflightPromise || http('/web/webclient/version_info', {}).then(function (reason) {
					odooRpc.shouldManageSessionId = (reason.result.server_serie < "8"); //server_serie is string like "7.01"
					preflightPromise = $q.when(); //runonce
				});
			}

			return preflight().then(function () {
				return http(url, params).then(function(response) {
					var subRequests = [];
					if (response.type === "ir.actions.act_proxy") {
						angular.forEach(response.action_list, function(action) {
							subRequests.push(http(action['url'], action['params']));
						});
						return $q.all(subRequests);
					} else
						return response.result;
				});
			});
		};

		return odooRpc;
	}];
});

