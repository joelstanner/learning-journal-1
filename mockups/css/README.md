Dat CSS [![npm version](http://img.shields.io/npm/v/datcss.svg?style=flat-square)](https://npmjs.org/package/datcss "View this project on npm") [![Dependency Status](https://david-dm.org/datcss/base.svg?style=flat-square)](https://david-dm.org/datcss/base)
==========

__A stylesheet for text-first, responsive websites.__



Principles
----------

### Unobtrusive
[At its heart, web design should be about words](http://justinjackson.ca/words.html). Dat CSS is deliberately built to highlight the quality of the text, and does it's best to conform to [IA's](https://ia.net/) [100% Easy-2-Read Standard.](https://ia.net/blog/100e2r/)

By default, HTML is responsive and attractive. Dat CSS provides a minimal set of styles that augments, rather than mask, the benefits natively provided by browsers. Rather than rewriting everything from scratch, Dat CSS serves as a layer on top of what already exists.

Dat CSS is extremely lightweight, clocking at only XXKb.


### Understandable
Dat CSS was developed to be modified and extended. The codebase is simple, modular, and well-commented so that Developers can get up and running quickly.

[In the spirit of simplicity](http://blog.keithcirkel.co.uk/why-we-should-stop-using-grunt/) Dat CSS relies on NPM for builds.

[Dat CSS is post-processed](https://github.com/postcss/postcss#why-postcss-better-than-), meaning that Developers need only write native CSS, rather than learning any of the preprocessed languages such as SASS, LESS, or Stylus.


### Maintainable
Dat CSS is heavily modularized, meaning components can be easily swapped in and out as required.

Dat CSS makes heavy use of Object-Oriented CSS, which we've found dramatically benefits maintainability, especially across large, collaborative codebases.




Usage
-----

[Install NPM](https://docs.npmjs.com/getting-started/installing-node).

```
npm install datcss
```

Include the following in your `<head>`

```
<link rel='stylesheet' href='/node_modules/datcss/index.css'>
```

### Variables
Modify `src/index/css`.

The following variables can be changed.

```css
	/* TYPOGRAPHY */
	--ms3: ;
	--ms2: ;
	--ms1: ;
	--ms0: ;
	--copy-font:	;
	--copy-font-weight: ;
	--copy-font-color:	;
	--heading-font: ;
	--heading-font-color: ;
	--heading-font-weight: ;
	--monospace-font: ;
	--line-height: ;
	--font-weight-light: ;
	--font-weight-book:	;
	--font-weight-medium: ;
	--font-weight-semibold: ;
	--font-weight-bold: ;
	--font-weight-black: ;

	/* LINKS */
	--link-color: ;
	--link-color-hover: ;

	/* LAYOUT */	
	--container-width: ;
```

Inspiration
-----------

- [BASSCSS](http://www.basscss.com/)
- [Tachyons](http://tachyons.io/)

