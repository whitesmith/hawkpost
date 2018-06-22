'use strict';

/* Usage:
 *
 *   gulp [watch]
 *     For development with live reload (default task).
 *
 *   gulp build
 *     Development build.
 *
 *   gulp build --production
 *     TODO: Production-ready build (asset concatenation, minification, ...).
 */

/* Gulp dependencies */
var gulp = require('gulp');
var runSequence = require('run-sequence');
var gutil = require('gulp-util');
var del = require('del');
var gulpif = require('gulp-if');

var notify = require('gulp-notify');

var argv = require('yargs').argv;

/* CSS */
var sass = require('gulp-sass');
var bulkSass = require('gulp-sass-bulk-import');
var moduleImporter = require('sass-module-importer');
var autoprefixer = require('gulp-autoprefixer');
var sourcemaps = require('gulp-sourcemaps');

/* Livereload */
var browserSync = require('browser-sync');

function handleError(task) {
  return function (err) {
    notify.onError({
      message: task + ' failed, check the logs..',
      sound: false
    })(err);

    gutil.log(gutil.colors.bgRed(task + ' error:'), gutil.colors.red(err));
    this.emit('end');
  };
}

/* Arguments: read the `production` env flag. */
var production = !!argv.production;

var sourcePaths = {
  stylesheets: "./stylesheets/",
};

var buildPath = "./hawkpost/static/";

var tasks = {};

tasks.browser_sync = function () {
  var config = {
      proxy: {
          target: "http://localhost:8000",
          ws: true
      },
      ghostMode: {
        clicks: false,
        location: false,
        forms: false,
        scroll: false
      }
  };

  browserSync(config);
};

tasks.clean = function (cb) {
  return del([buildPath + "style.css"], cb);
};

tasks.sass = function () {
  return gulp.src(sourcePaths.stylesheets + '*.scss')
    /* Sourcemaps + SASS */
    .pipe(gulpif(!production, sourcemaps.init()))
    .pipe(bulkSass())
    .pipe(sass({
      importer: moduleImporter(),
      sourceComments: !production,
      outputStyle: production ? 'compressed' : 'nested'
    }))
    .on('error', handleError('SASS'))
    /* Generate .maps */
    .pipe(gulpif(!production, sourcemaps.write({
      includeContent: false,
      sourceRoot: '.'
    })))
    .pipe(gulpif(!production, sourcemaps.init({
      loadMaps: true
    })))
    /* Autoprefixer */
   .pipe(autoprefixer({
      browsers: ['last 2 versions'],
    }))
    /* We don't serve the source files,
     * so include SCSS content inside the sourcemaps. */
    .pipe(sourcemaps.write({
      includeContent: true
    }))
    .pipe(gulp.dest(buildPath + 'css/'))
    .pipe(browserSync.reload({ stream: true }));
};

/* Compilation tasks */
gulp.task('clean', tasks.clean);

gulp.task('sass', tasks.sass);

/* Assets compilation and reload. */
gulp.task('browser-sync', tasks.browser_sync);
var browserSyncRefresh = browserSync.reload.bind(browserSync);
var browserSyncStream  = function () { browserSync.reload({ stream: true }); };

gulp.task('reload-sass', ['sass'], browserSyncStream);

/* Watch task */
gulp.task('watch', function (cb) {
  return runSequence(
    'build',
    'browser-sync',
    function () {
      /* Avoiding the compilation of the vendor styles on save, faster faster faster! */
      gulp.watch(sourcePaths.stylesheets + '**/*.scss', ['reload-sass']);

      gutil.log(gutil.colors.bgGreen('Watching for changes...'));
      return cb();
    }
  );
});

/* Build task */
gulp.task('build', function (cb) {
  /* Clean first, build afterwards. */
  return runSequence(
    'clean', [
      'sass',
    ], cb);
});

/* Default task (`watch`) */
gulp.task('default', ['watch']);
