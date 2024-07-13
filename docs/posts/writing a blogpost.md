---
comments: true
date: 2024-07-13
authors:
    - Toebias-HT
categories:
    - Tutorial
---
![image](https://raw.githubusercontent.com/Pykampala-Community/assets/main/pykampala4.png)

## Welcome to Pykampala's community blog
<b>
Welcome to the python kampala community blog. In this blog post, I share how to write and contribute 
your blog post to this community channel.
</b>
<!-- more -->
To start with, I'm excited that we've set up our first blog channel. This is the first milestone 
to building our web presence. We've previously been more active on our Whatsapp platform as with other
Ugandan communities. Attempts to adopt other platforms such as telegram and discord have failed for varying reasons.
This is however a next step to open up our community engagement beyond the limited whatsapp platform.
With blog posts, you can share your ideas and knowledge to a wider python community audience.

## Infrastructure
This blog channel is set up using material for mkdocs. Material for mkdocs offers a rich set of features that are 
useful for building an engaging blog channel. The other alternative for building our blog channel would have been to use
platforms such as `hashnode` and `dev.to` but we found the need to utilize existing python tools, if any, to build our blog.
The longer attempt would have been to implement our own blog technology from scratch with Javascript and Python, but that 
would have taken months to get right.

We use gisus for the comments. [Giscus](https://giscus.app/) is a free and open source JS library to help you transform github discussions into a powerful comment section. You can write comments in markdown and review them on the discussions repository.
In order to write a comment, you have to sign into github and allow the Giscus tool to post to the discussions repository on
your behalf. You can track your comment and more on the [discussions](https://github.com/orgs/Pykampala-Community/discussions/categories/comments) repository.

## Publishing your post
To publish your blog post, fork the [blogs](https://github.com/Pykampala-Community/blogs) repository. Inside the blog repo, there's a folder called posts containing markdown files. Create a new markdown file for your post and give it a short but descriptive name, for example "Error handling in python.md" or "When to use Polars instead of Pandas.md". This name will be used as the title for your blog post. Write your post following the format described in the 
sections below. After confirming that your post is properly written, make a pull request to the blog repo. The admin will evaluate the post and merge it to the main repository. The github actions pipeline will then automatically rebuild the blogs site with your new blog post included. The results will typically reflect in a few seconds.

## Front matter
Now let's focus on the content of your markdown file. Typically, your markdown file will start with a header sections containing some yaml configuration settings. This header section is what we call the `front matter` and it's the first section of the markdown file.
The front matter starts with tripple hyphen followed by the yaml configuration and then ends with the tripple hyphen
```
---
yaml
---
```
After the front matter has been included, you can go ahead and write your blog body in markdown format.

## Body
The body of the blog post is written in markdown. However, we can use the extra functionality provided by material for mkdocs to add features such as buttons, data tables, grids, tabs and more to our blog posts.
We can go ahead and include limited use of HTML and CSS to our blog posts in areas where it's necesarry, for example in the abstract. There are 3 main parts of the body.

* The blog image: This will be placed after the blog title.
* The blog abstract: This is an excerpt that gives a highlight of the blog post. It is the first thing a reader reads to give then a brief of the blog content before diving in.
* The main content: This contains details written by the writer intended for the user.

**The body image** should be the first item before writing the rest of your body. It can simply be included using markdown
syntax `![image](url)`. The url can point to any resource where an image can be requested. No external multimedia should be embedded directly into the blog post.

**The abstract** should follow the image. The abstract contains a title and excerpt. The title is an `h2` header text. You can use markdown `##` as a prefix to the title name for the `h2` header.
The excerpt should be written in bold. It should be a description of what the reader expects to read. It should be written like
```html
<b>
   description of the blog post
</b>
<!-- more -->
```
The `<!-- more -->` is used to signal to the reader that there's more to read beyond the abstract.

**The main content** can now follow the rest of the body of the blog post

## Configuration
Like we mentioned earlier, you can add yaml configuration to your blog post in the front matter to activate or deactivate certain properties of your blog. For now, there are only 4 properties to focus on, that is:

- date
- comments
- authors
- categories

**date** is written in the format `year-month-day`. This is an required property and should be wriiten for every blog post submitted via pull request. For example `2024-07-13` shows that this blog post was published on this date.

**comments** are a boolean value that should always be true.
`comments: true`

**categories** is can be any option or even all among:

    - Tutorial
    - Benchmark
    - Performance
    - Data
    - Ai
    - Project
    - General

Example
```
categories:
    - Tutorial
    - Benchmark
```

**Authors:** Adding authors requires you to first modify the `.authors.yml` file located in the posts directory. Add a new entry under the authors property in the format
```
authors:
    identifier:
        name: "name"
        description: "Short description of yourself"
        avatar: url-to-github-display-picture
```

After successfully adding the entry in the `.authors.yml` file, you can now apply it to your blog post under the `authors` property.
```
authors:
    - identifier
```

## Example blog post
```
file name: An async web-server.md

---
data: 2024-07-22
comments: true
authors:
    - Toebias-HT
categories:
    - Tutorial
---
![image](url)
## Building a non-blocking webserver with Asyncio
<b>
    Asyncio is a library that helps you leverage the power of asynchronous programming
    to build high throughput and fast executing web servers. In this blog post, I share
    how yo can leverage asyncio to build a server that can handle upto 100,000 connections
</b>
<!-- more -->
[body]
```
## Conclusion
This blog channel is powered by mkdocs and material-for-mkdocs. To understand more about the various configuration and setup read through the [docs](https://squidfunk.github.io/mkdocs-material/setup/setting-up-a-blog/)