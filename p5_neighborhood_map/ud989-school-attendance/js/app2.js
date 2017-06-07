var model = {
  days: 12,
  students: [
              {
                name: "Slappy the Frog",
                attendance: Array(this.days).fill(0),
              },
              {
                name: "Lilly the Lizard",
                attendance: Array(this.days).fill(0),
              },
              {
                name: "Paulrus the Walrus",
                attendance: Array(this.days).fill(0),
              },
              {
                name: "Gregory the Goat",
                attendance: Array(this.days).fill(0),
              },
              {
                name: "Adam the Anaconda",
                attendance: Array(this.days).fill(0),
              }
  ],
};

var octopus = {

};

var attendanceTable = {
  init: function() {
    // create columns for the number of days
    for (i=0; i < model.days; i++) {
      var day = i + 1;
      $('#table-header th:last-child').before('<th>' + day + '</th>');
    };
    console.log(model.students)
    // create columns for students with rows for days and days missed
    for (i=0; i < model.students.length; i++) {
      // creates table rows
      row = '<tr></tr>'
      $(row).appendTo('tbody').addClass("student");
      for (j=0; j < model.days; j++) {
        row.append('<td></td>');
      }
    };

  }

}

function renderStudent(student) {
  result = `<td>${student.name}</td>`;
  result += student.attendance.map(function(record) { return `<td>${record === 1 ? "checkmark" : ""}</td>`} ).join('');
}

attendanceTable.init();
