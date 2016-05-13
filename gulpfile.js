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

var path = require('path');
var gulp = require('gulp');
var runSequence = require('run-sequence');
var gutil = require('gulp-util');
var del = require('del');
var gulpif = require('gulp-if');
var exec = require('child_process').exec;

var notify = require('gulp-notify');
var plumber = require('gulp-plumber');

var buffer = require('vinyl-buffer');
var argv = require('yargs').argv;

// sass
var sass = require('gulp-sass');
var bulkSass = require('gulp-sass-bulk-import');
var moduleImporter = require('sass-module-importer');
var autoprefixer = require('gulp-autoprefixer');
var sourcemaps = require('gulp-sourcemaps');
var minifyCSS = require('gulp-clean-css');
var concat = require('gulp-concat');
var imagemin = require('gulp-imagemin');


// BrowserSync
var browserSync = require('browser-sync');

var deploy = require('gulp-deploy-git');

/* Read the `production` env flag. */
var production = !!argv.production;

var sourcePaths = {
  stylesheets: "./stylesheets/",
};

var buildPath = "./hawkpost/static/";

// ----------------------------
// Error notification methods
// ----------------------------
var beep = function() {
  var os = require('os');
  var file = 'gulp/error.wav';
  if (os.platform() === 'linux') {
    // linux
    exec("aplay " + file);
  } else {
    // mac
    console.log("afplay " + file);
    exec("afplay " + file);
  }
};

var handleError = function (task) {
  return function (err) {
    beep();

    notify.onError({
      message: task + ' failed, check the logs..',
      sound: false
    })(err);

    gutil.log(gutil.colors.bgRed(task + ' error:'), gutil.colors.red(err));
    this.emit('end');
  };
};

var tasks = {};

tasks.browser_sync = function () {
  var config = {
      proxy: {
          target: "http://0.0.0.0:8000",
          ws: true
      },
      ghostMode: {
        clicks: false,
        location: false,
        forms: false,
        scroll: false
      }
  }
  //run TUNNEL=true gulp to start public tunnel url to share.
  if (process.env.TUNNEL === 'true') {
    config.tunnel = "qoldwebapp";
  }

  browserSync(config);
};

tasks.clean = function (cb) {
  return del([buildPath + "style.css"], cb);
};


// --------------------------
// SASS (libsass)
// --------------------------
tasks.sass = function() {
  return gulp.src(sourcePaths.stylesheets + '*.scss')
    // sourcemaps + sass + error handling
    .pipe(gulpif(!production, sourcemaps.init()))
    .pipe(bulkSass())
    .pipe(sass({
      importer: moduleImporter(),
      sourceComments: !production,
      outputStyle: production ? 'compressed' : 'nested'
    }))
    .on('error', handleError('SASS'))
    // generate .maps
    .pipe(gulpif(!production, sourcemaps.write({
      includeContent: false,
      sourceRoot: '.'
    })))
    // autoprefixer
    .pipe(gulpif(!production, sourcemaps.init({
      loadMaps: true
    })))
   .pipe(autoprefixer({
          browsers: ['last 2 versions'],
    }))
    /* We don't serve the source files
     * so include scss content inside the sourcemaps. */
    .pipe(sourcemaps.write({
      includeContent: true
    }))
    .pipe(gulp.dest(buildPath + 'css/'))
    .pipe(browserSync.reload({stream: true}));
};



tasks.fonts = function() {
  return gulp.src(sourcePaths.assets + 'fonts/**/*.*')
    .pipe(gulp.dest(buildPath + 'assets/fonts/'));
};

tasks.images = function() {
  return gulp.src(sourcePaths.assets + 'images/**/*.*')
  .pipe(gulpif(production, imagemin({progressive: true})))
  .pipe(gulp.dest(buildPath + 'assets/images/'))
};

/* Compilation tasks */
gulp.task('clean',         tasks.clean);

gulp.task('sass',          tasks.sass);
gulp.task('views',         tasks.views);
gulp.task('fonts',         tasks.fonts);
gulp.task('images',        tasks.images);

/* Assets compilation and reload. */
gulp.task('browser-sync', tasks.browser_sync);
var browserSyncRefresh = browserSync.reload.bind(browserSync);
var browserSyncStream  = function () { browserSync.reload({ stream: true }) };


gulp.task('reload-sass',      ['sass'],          browserSyncStream);
gulp.task('reload-vendor',    ['vendor-styles'], browserSyncStream);
gulp.task('reload-fonts',     ['fonts'],         browserSyncRefresh);
gulp.task('reload-images',    ['images'],        browserSyncRefresh);

gulp.task('reload-pages', function () {
  browserSyncRefresh();
});

/* Watch task */
gulp.task('watch', function (cb) {
  return runSequence(
    'build',
    'browser-sync',
    function () {
      /* Avoiding the compilation of the vendor styles on save, faster faster faster! */
      gulp.watch([
              sourcePaths.stylesheets + '**/*.scss',             ], ['reload-sass']);
      gulp.watch(sourcePaths.assets      + 'fonts/',                               ['reload-fonts']);
      gulp.watch(sourcePaths.assets      + 'images/',                              ['reload-images']);

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
      'fonts',
      'images'
    ], cb);
});

/* Default task (`watch`) */
gulp.task('default', ['watch']);


/*
 * GH pages deploy
 * --------------- */

gulp.task('gh-pages', function() {
  return gulp.src(buildPath + '**/*')
    .pipe(deploy({
      prefix: 'dist',
      repository: 'github_repo_url',
      remoteBranch: ['gh-pages']
    }));
});

gulp.task('deploy', function(cb) {
  return runSequence(
    'build',
    'gh-pages',
  cb);
});
