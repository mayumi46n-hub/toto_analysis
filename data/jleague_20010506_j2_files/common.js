$(document).ready(function(){
	var beforeunloadFlag = 0;
	$(window).bind('beforeunload', function(event){
		beforeunloadFlag = 1;
	});
	var fail = function(jqXHR, textStatus, errorThrown) {
		if (beforeunloadFlag === 0 && jqXHR.status === 0 && textStatus === 'error') {
			$.showAsDialog(serverAccessErrorMessage, {
				title: serverAccessErrorTitle
			});
		} else if (beforeunloadFlag === 1 && jqXHR.status === 0 && textStatus === 'error'){
			
		} else {
			$.showAsDialog(processingErrorMessage, {
				title: processingErrorTitle
			});
		}
	};
	
	var target = [
		'#gnav-area ul#gnav li a',
		'#contents-side ul.game-base li a',
		'.tab-box ul li a',
		'.slide-box .slide-child li a',
		'ul.score-btn li a'
	];
	var len = target.length;

	$('#header-area li#hnav-login .hnav-login-bg-r a').hover(
		function(){ $(this).parents('li#hnav-login').addClass('hover'); },
		function(){ $(this).parents('li#hnav-login').removeClass('hover'); }
	);

	$('#header-area li#hnav-login-en .hnav-login-bg-r a').hover(
			function(){ $(this).parents('li#hnav-login-en').addClass('hover'); },
			function(){ $(this).parents('li#hnav-login-en').removeClass('hover'); }
		);

	for(var i = 0; i < len; i++) {
		$(target[i]).hover(
			function(){ $(this).parent().addClass('hover'); },
			function(){ $(this).parent().removeClass('hover'); }
		);
	}

	$('.slide-btn').mouseover(function() {
		$(this).parent().find('.slide-child').slideDown('slow').show();
		$(this).parent().hover(function() {
		}, function(){
			$(this).parent().find('.slide-child').slideUp('fast');
		});
		}).hover(function() {
			$(this).addClass('hover');
		}, function(){
			$(this).removeClass('hover');
	});


	var w = $('.table-over-box').width();
	$('.table-over-box').width(w);

	$('.standings-table-box .table-over-box .wd00').width(74);
	$('.standings-table-box .table-over-box .wd01').width(95);
	$('.standings-table-box .table-over-box > table').width(84 + ($('.standings-table-box .table-over-box .table-head .wd01').length)*95);
	
	$('.year-visitor-table-box table tfoot , .year-visitor-table-box table tbody').find('td:nth-child(3n)').addClass('bd-l');
	$('.year-visitor-table-box .table-over-box .wd00').width(81);
	$('.year-visitor-table-box .table-over-box .wd01').width(142);
	$('.year-visitor-table-box .table-over-box .wd02').width(142);
	$('.year-visitor-table-box .table-over-box > table').width(223 + ($('.year-visitor-table-box .table-over-box .wd02').length*143));
	
	$('.club-table-box table.child').find('td:nth-child(n+2)').addClass('bd-l');
	$('.club-table-box table.child').find('tr:last td').addClass('bd-none');
	$('.club-table-box .table-over-box .wd00').width(68);
	$('.club-table-box .table-over-box .wd01').width(99);
	//$('.club-table-box .table-over-box thead .wd02').width(99);
	$('.club-table-box .table-over-box .wd02').width(88);
	//$('.club-table-box .table-over-box > table').width(139 + ($('.club-table-box .table-over-box thead .wd01').length*100));

	$('.record-table-box-index .table-over-box thead .wd00').width(191);
	$('.record-table-box-index .table-over-box thead .wd01').width(40);
	$('.record-table-box-index .table-over-box thead .wd02').width(56);
	$('.record-table-box-index .table-over-box > table').width(231 + ($('.record-table-box-index .table-over-box thead .wd02').length*59));

	$('.record-table-box-warnings .table-over-box thead .wd00').width(137);
	$('.record-table-box-warnings .table-over-box thead .wd01').width(102);
	$('.record-table-box-warnings .table-over-box thead .wd02').width(47);
	$('.record-table-box-warnings .table-over-box thead .wd03').width(102*0.3);
	$('.record-table-box-warnings .table-over-box > table').width(239 + ($('.record-table-box-warnings .table-over-box .thead .wd02').length*50));

	$('[placeholder]').ahPlaceholder({
		placeholderColor : 'silver',
		placeholderAttr : 'placeholder',
		likeApple : false
	});

	$.extend({
		json: function(opts) {
			var spin = $('#spin').spin();
			return $.ajax($.extend({
				dataType: 'json',
				scriptCharset: 'utf-8',
				type: 'POST'
			}, opts)).done(function(data) {
				if (opts.url != '/login' && data.error) {
					var message = '<ul class="errors" style="margin-left: 0.5em;">'
					if (data.messages) {
						var len = data.messages.length;
						for (var i = 0; i < len; i++) {
							message += '<li>' + data.messages[i] + '</li>';
						}
					} else {
						message += '<li>' + processingErrorMessage + '</li>';
					}
					message += '</ul>'
					$.showAsDialog(message, {
						title: processingErrorTitle
					});
				}
			}).fail(fail).always(function() {
				spin.spin();
			});
		},
		loadAsDialog: function(ajaxOpts, dialogOpts) {
			var spin = $('#spin').spin();
			return $.ajax($.extend({
				dataType: 'html',
				scriptCharset: 'utf-8',
				type: 'POST'
			}, ajaxOpts)).done(function(data) {
				$dialog = $('<div>' + data + '</div>');
				$dialog.showAsDialog($.extend({
					close: function(e) {
						$dialog.dialog('destroy');
						$(e.target).remove();
					}
				}, dialogOpts));
			}).fail(fail).always(function() {
				spin.spin();
			});
		},
		showAsDialog: function(message, opts) {
			$('<div>' + message + '</div>').showAsDialog(opts);
		},
		openStadiumSearchDialog: function(stadiumIds, callback) {
			var stadiumSearchWindow = window.open("about:blank", 'stadiumSearch', 'width=780, height=580, menubar=no, toolbar=no, scrollbars=yes');
			window.onStadiumSelect = callback;
			var form = $('<form action="/SFCM02/" method="POST" target="stadiumSearch" />');
			stadiumIds = stadiumIds || [];
			var len = stadiumIds.length
			for (var i = 0; i < len;  i++){
				form.append('<input type="hidden" name="stadium_ids[' + i + ']" value="' +stadiumIds[i] +'" />');
			}
			$('body').append(form);
			form.submit();
			form.remove();
		}
	});

	$.fn.toSmartDevice = function(options) {
	    return this.each(function() {
	    	var $select = $(this).hide();
	    	var name = $select.attr("name");
	    	var $checkboxes = $select.next("div#"+name+"-check");
	    	if($checkboxes.length == 0){
	    		$checkboxes = $("<div><ul/></div>")
	    		$checkboxes.attr("id", name+"-check");
	    		$checkboxes.attr("class", $select.attr("class"));
		    	$select.after($checkboxes);
	    	}
	    	var $list = $("ul", $checkboxes);
	    	$list.empty();
	    	$("option", $select).each(function(j){
	    		var $option = $(this);
	    		var id = $select.prop("name") + $option.val();
	    		var $checkbox = $("<input />").attr({
	    			"id"   :  id,
	    			"type" : "checkbox"
	    		}).prop({
	    			"checked"  : $option.prop("selected")
	    		}).change(function(e){
	    			$option.prop("selected", $checkbox.prop("checked"));
	    			$select.trigger("change");
	    		});
	    		var $item = $("<li/>")
	    			.append($checkbox)
	    			.append(
	    				$("<label />").attr({
	    					"for" : id
	    				}).append(
	    					$option.text()
	    				)
	    		);
	    		$list.append($item);
	    	});
	    });
	}
	$("select[multiple]").toSmartDevice();

	$.fn.sortTable = function(options) {
		if(!$.fn.tablesorter) return;

		var options = $.extend({
			printPage : false,
			selectorHeader : "thead tr",
			selectorHeaders : (options && options.selectorHeader) ? options.selectorHeader + " th" : $.tablesorter.defaults.selectorHeaders
		}, options);

		return this.each(function() {
			$table = $(this);
			var headers = new Object();
			var sortAppendCond = new Object();
			var thCount = 0
			var sorterList = new Object;
			$(options.selectorHeader, $table).each(function(rowIndex,rowItem){
				$("th", $(rowItem)).each(function(index,item){
					var $item = $(item);
					var type = $item.data("sort-type");
					if(type){
						headers[thCount] = { sorter : type };
						sorterList[index] = {headers : thCount};
					} else{
						headers[thCount] = { sorter : false };
					}

					var append = $item.data("sort-append");
					if(append){
						 sortAppendCond[append] = { col:index, order: 0};
					}
					thCount = thCount + 1;
				});
			});

			var sortAppend = new Array();
			$.each(sortAppendCond, function(index,item){
				sortAppend.push([item.col, item.order]);
			});
			
			var sortList = new Array();
			if(options && options.sortList && options.sortList.length) {
				$.each(options.sortList, function(index,item){
					sortList.push(item);
				});
				$.each(sortAppend, function(index,item){
					sortList.push(item);
				});
			}

			$table.tablesorter($.extend({}, options, {
				headers: headers,
				sortList: sortList,
				sortAppend : sortAppend
			})).bind("headersCssEnd", function(e) {
				var config = this.config;
				var sortList = this.config.sortList;
				var userSelect = sorterList[sortList[0][0]].headers;
				for(var i = 1; i < config.headerList.length; i++){
					if (i != userSelect) {
						$(config.headerList[i]).removeClass(config.cssDesc).removeClass(config.cssAsc);
					}
				}
			});
			
			if(options.printPage){
				$(options.selectorHeader, $table).children("th").unbind("click");
			}
		});
	};
});