var gulp                = require('gulp')
var postcss             = require('gulp-postcss')
var autoprefixer        = require('autoprefixer-core')
var atImport            = require('postcss-import')
var customProperties    = require('postcss-custom-properties')
var fontVariants        = require('postcss-font-variant')
var customMedia         = require('postcss-custom-media')
var rename              = require('gulp-rename')
var minify              = require('gulp-minify-css')


gulp.task('build', function () {
    var processors = [
        atImport(),
        fontVariants(),
        autoprefixer({ browsers: ['last 3 versions']}),
        customProperties(),
        customMedia()
    ];
    return gulp.src('./src/index.css')
        .pipe(postcss(processors))
        .pipe(gulp.dest('./'))
        .pipe(minify())
        .pipe(rename('index.min.css'))
        .pipe(gulp.dest('./'))
})

gulp.task('watch', function () {
    gulp.watch('src/*.css', ['build'])
})

gulp.task('default', ['watch'])
