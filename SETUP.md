# Set up the base image

Run these commands from this repository's root. The image is shared by both tasks.

## On the original development machine

The pinned image is already available under an earlier name. With Docker running:

```sh
docker tag better-auth-string-roundtrip:base better-auth-tasks:base
python3 run_demo.py wildcard
```

## On another machine

Build the image from a clean upstream checkout. This step needs internet access and may take a few minutes.

```sh
mkdir -p .work
git clone https://github.com/better-auth/better-auth.git .work/better-auth
git -C .work/better-auth checkout e7200d132f5946490c19a389b5a89b31aeead4e7
cp Dockerfile .work/better-auth/Dockerfile
cp upstream.dockerignore .work/better-auth/.dockerignore
docker build -t better-auth-tasks:base .work/better-auth
python3 run_demo.py all
```

The Dockerfile pins the Node image and package-manager version. The upstream lockfile pins project dependencies. It builds from the original source without either task's patches. Test and reference patches are applied only during the replay.

The replay checks the affected starting files, runs as a non-root user, and disables networking. It records failures as well as passes. Python needs write access to the report folder.

If the image is unavailable, the demo reports the Docker error. If the code or test counts differ, it stops rather than reporting a successful replay.
