import argostranslate.package as p
p.update_package_index()
x=[x for x in p.get_available_packages() if (x.from_code,x.to_code)==('en','zh')][0]
print('downloading',x,flush=True)
path=x.download()
print('downloaded',path,flush=True)
p.install_from_path(path)
print('installed',flush=True)
