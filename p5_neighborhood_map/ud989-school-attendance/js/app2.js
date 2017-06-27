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

var controller = {

  getDays: function() {
    return model.days;
  },

  getStudents: function() {
    return model.students;
  },

  init: function() {
    attendanceTable.init();
  }
};

var attendanceTable = {
  init: function() {
    var students = controller.getStudents();
    var student = students[1];
    var days = controller.getDays();
    this.renderHeader();
    this.renderStudent(student);
  },

  renderHeader: function() {
    for (i=0; i < model.days; i++) {
      var day = i + 1;
      $('#table-header th:last-child').before(`<th>${day}</th>`);
    };
  },

  renderStudent(student) {
    studentRow = '<tr></tr>';
    $(studentRow).appendTo('tbody').addClass("student");
    studentData = `<td>${student.name}</td>`
    $(studentRow).append(studentData);
  }

    // create columns for the number of days

    // // create columns for students with rows for days and days missed
    // for (i=0; i < model.students.length; i++) {
    //   // creates table rows
    //   row = '<tr></tr>'
    //   $(row).appendTo('tbody').addClass("student");
    //   for (j=0; j < model.days; j++) {
    //     row.append('<td></td>');
    //   }
    // };

}

function renderStudent(student) {
  result = `<td>${student.name}</td>`;
  result += student.attendance.map(function(record) { return `<td>${record === 1 ? "checkmark" : ""}</td>`} ).join('');
}

controller.init();
