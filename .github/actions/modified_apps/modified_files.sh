if [ $GITHUB_EVENT_NAME == 'pull_request' ]; then
    echo "changed_files=$(git diff --name-only -r HEAD^1 HEAD | xargs)" >> $GITHUB_OUTPUT
else
    echo "changed_files=$(git diff --name-only $GITHUB_EVENT_BEFORE $GITHUB_EVENT_AFTER | xargs)" >> $GITHUB_OUTPUT
fi