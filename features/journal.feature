Feature: Journal
    Implement a CRU-able Learning Journal



    Scenario: At least a cat
        Given that I am a user
        When I visit the index page and there are no entries
        Then I should see a cat

    Scenario: At most, posts
        Given that I am a user
        When I visit the index page and there are entries
        Then I should see a list of the entries

    Scenario: 404
        Given that I am a user
        When I visit attempt to visit a page that doesn't exist
        Then I am redirected to the 404 cat-page

    Scenario: View a post
        Given that I am a user
        When  I click a link of a post title
        Then I see the correct post page

    Scenario: Code formatting
        Given that I am user
        When I view a page
        Then code blocks should be colorized



    Scenario: Not an admin
        Given that I am a user
        When I view a post entry
        Then I should not see an edit button

    Scenario: An admin
        Given that I am an admin
        When a view a post entry
        Then I should see an edit button

    Scenario: Save things
        Given that I am an admin
        When a edit a post entry
        Then I should be able to save it

    Scenario: Markdown
        Given that I am an admin
        When I visit an edit-able page
        Then I should be able to write my content in Markdown

    



