var cardWidth = 0;
var sound_state = true;

$(window).on("load", function() {
	initRotatedBackgroundCards();
	$(".player-form").submit(function(e) {
		e.preventDefault();
		postPlayerForm($(this));
	});
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
					$("#passed-tasks").prepend(response.passed);
					if (sound_state) $("#" + response.audio)[0].play();
				}
				if (response.form || response.answer) if (play) play();
			} 
		}
	});
}

function setSound(state) {
	sound_state = state;
	if (state) {
		$("#sound-state-on").removeClass("d-none").addClass("d-inline");
		$("#sound-state-off").removeClass("d-inline").addClass("d-none");
	} else {
		$("#sound-state-on").removeClass("d-inline").addClass("d-none");
		$("#sound-state-off").removeClass("d-none").addClass("d-inline");
	}
	$("#collapse-sound").collapse("toggle");
	$("#collapse-sound-frame").collapse("toggle");
}

function setShow(state) {
	if (state) {
		$("#show-state-answers").removeClass("d-none").addClass("d-inline");
		$("#show-state-nothing").removeClass("d-inline").addClass("d-none");
		$("#passed-tasks").removeClass("d-none");
	} else {
		$("#show-state-answers").removeClass("d-inline").addClass("d-none");
		$("#show-state-nothing").removeClass("d-none").addClass("d-inline");
		$("#passed-tasks").attr("class", "d-none");
	}
	$("#collapse-show").collapse("toggle");
	$("#collapse-show-frame").collapse("toggle");
}