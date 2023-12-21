      // `atob` won't decode utf8 characters correctly, we need to do more about this
      // taken from this excellent answer https://stackoverflow.com/a/30106551
      function b64DecodeUnicode(str) {
        return decodeURIComponent(
          atob(str)
            .split('')
            .map(function (c) {
              return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
            })
            .join('')
        )
      }

      async function fetch_ipynb_content_raw(url) {
        if (input_url.startsWith('https://raw.githubusercontent.com')) {
          api_url = input_url
        } else {
          // extract relevant bits from the URL and create a URL for the Github API
          const ghparts = new RegExp(
            /https:\/\/github.com\/(.+?)\/(.+?)\/blob\/(.+?)\/(.+\.ipynb)/
          )
          const m = input_url.match(ghparts)
          if (!m) {
            // TODO: render some placem
            console.error('invalid URL ' + input_url)
            return
          }
          filename = m[4].split('/').pop()
          filename = decodeURI(filename)
          api_url = `https://raw.githubusercontent.com/${m[1]}/${m[2]}/${m[3]}/${m[4]}`

          // const api_url = `https://api.github.com/repos/${m[1]}/${m[2]}/contents`
          console.log(`translated ${input_url} into ${api_url}, fetching`)
        }

        const dd = await fetch(api_url) // TODO: this could fail on API limits
        const dt = await dd.json()
        return dt;
      }

      async function render_gh_files(input_url, filename) {
        console.log('rendering')
        // const hs = window.location.hash.slice(1); // without '#'
        // const hsurl = atob(hs); // base64 -> text

        let api_url;
        let dt;

        if (input_url.startsWith('https://api.github.com/')) {
          // extract relevant bits from the URL and create a URL for the Github API
          const dd = await fetch(input_url);
          dt = await dd.json();

          const content = atob(dt["content"]);
          dt = JSON.parse(content);
        }
        else if (input_url.startsWith('https://raw.githubusercontent.com') || input_url.startsWith('https://github.com')) {
          dt = await fetch_ipynb_content_raw(input_url);
        }


        tg = document.createElement('div')
        tg.setAttribute('class', 'rendered-notebook')
        tg.setAttribute('rel', input_url)

        const notebook_content = document.getElementById('notebook-content')
        // clear previous input
        notebook_content.innerHTML = ''
        notebook_content.appendChild(tg)

        notebook_viewer.render(dt, tg)

        // document.getElementById('download-notebook').style.display = 'block'

        document.getElementById(
          'serving-info'
        ).innerHTML = `Serving <code>${filename}</code>. <a href='https://github.com/${target_repo}/blob/master/${filename}'>Github Source</a>`
        return
      }