var cardWidth = 0;
var sound_state = true;

$(window).on("load", function() {
	localizeTimestamp();
	initRotatedBackgroundCards();
	$(".player-form").submit(function(e) {
		e.preventDefault();
		postPlayerForm($(this));
	});
	$(".info-page").modal("show");
	$(".info-page-closer").on("click", function(){ $(".info-page").modal("hide"); });
	$(".feedback-form").submit(function(e) {
		e.preventDefault();
		postFeedbackForm($(this));
	});
	$(".button-click").click(function() {	$("#button-click")[0].play(); });
});

$(window).on("resize", function() {
	initRotatedBackgroundCards();
});

$(window).on("orientationchange", function() {
	initRotatedBackgroundCards();
});

function initRotatedBackgroundCards() {
	$(".rotated-background-card").each(function() {
		addRotatedBackgroundCard($(this));
	});
}

function addRotatedBackgroundCard(el) {
	var rect = $(el)[0].getBoundingClientRect();
	if (cardWidth != rect.width) {
		cardWidth = rect.width;
		$(".background-card").each(function() { $(this).remove(); });
		$(el).parent().prepend('<div class="background-card"></div>');
		$(".background-card").each(function() {
			$(this).attr(
				"class",
				$(el).attr("class").replace(
					"rotated-",
					"rotated-" + $(el).attr("angle") + " "
				)
			);
			$(this).css("width", rect.width);
			$(this).css("height", rect.height);
			$(this).css("position", "absolute");
			$(this).css("top", 0);
		});
	}
}

function postPlayerForm(el) {
	var formData = $(el).serialize();
	var controls = $("#" + $(el).attr("id") + " *").filter(":input");
	$(controls).each(function () { $(this).attr("disabled", true) });
	$.ajax({
		type: "post",
		url: $(el).attr("actions"),
		data: formData + "&ajax=1",
		success: function(response, status, xhr){ 
			var ct = xhr.getResponseHeader("content-type") || "";
			if (ct.indexOf('html') > -1) {
				window.document.write(response);
			}
			if (ct.indexOf('json') > -1) {
				if (response.redirect) location.pathname = response.redirect;
				if (response.form) $(el).html(response.form);
				if (response.passed) {
					$("#passedTasks").prepend(response.passed);
					if (sound_state) $("#" + response.audio).clone()[0].play();
				}
				if (response.progress) {
					$("#playerProgress").attr("style", "width: " + response.progress.percent + "%;");
					$("#playerProgressCurrent").html(response.progress.current);
					$("#playerProgressLeft").html(response.progress.left);
				}
				if (response.form || response.answer) if (play) play();
			} 
		},
		error: function (request, status, error) {
			location.pathname = "/";
		}
	});
}

function setSound(state) {
	sound_state = state;
	if (state) {
		$("#soundStateOn").removeClass("d-none");
		$("#soundStateOff").addClass("d-none");
	} else {
		$("#soundStateOn").addClass("d-none");
		$("#soundStateOff").removeClass("d-none");
	}
}

function setShow(state) {
	if (state) {
		$("#showStateAnswers").removeClass("d-none");
		$("#showStateNothing").addClass("d-none");
		$("#passedTasks").removeClass("d-none");
	} else {
		$("#showStateAnswers").addClass("d-none");
		$("#showStateNothing").removeClass("d-none");
		$("#passedTasks").addClass("d-none");
	}
}

function initTimezoneOffset(sessionTimezoneOffset) {
	var timezoneOffset = (new Date()).getTimezoneOffset();
	if (timezoneOffset.toString() != sessionTimezoneOffset) {
		$.ajax({
			type: "post",
			async: false,
			url: "/timezone",
			data: "timezoneOffset=" + timezoneOffset.toString(),
			success: function (data, textStatus, request) { console.log(data); }
		});
	}
}

function localizeTimestamp() {
	var user_tz = moment.tz.guess();
	moment.locale("{{ session['language'] }}");
	$(".timestamp").each(function() {
		this.innerText = moment(this.innerText).tz(user_tz).fromNow() + moment(this.innerText).tz(user_tz).format(', HH:mm:ss, DD MMMM YYYY, dddd');
	});
	$(".timestamp-short").each(function() {
		this.innerText = moment(this.innerText).tz(user_tz).fromNow();
	});
}

function postFeedbackForm(el) {
	var formData = $(el).serialize();
	var controls = $("#" + $(el).attr("id") + " *").filter(":input");
	$(controls).each(function () { $(this).attr("disabled", true) });
	$.ajax({
		type: "post",
		url: $(el).attr("actions"),
		data: formData ,
		success: function(response, status, xhr){ 
			var ct = xhr.getResponseHeader("content-type") || "";
			if (ct.indexOf('html') > -1) {
				window.document.write(response);
			}
			if (ct.indexOf('json') > -1) {
				if (response.redirect) location.pathname = response.redirect;
				if (response.message) {
					$(el).html(response.message);
					$(".feedback-close").removeClass("d-none");
				}
			} 
		},
		error: function (request, status, error) {
			location.pathname = "/";
		}
	});
}
